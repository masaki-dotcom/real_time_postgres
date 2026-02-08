<template>
  <input type="file" @change="onFile" />
  <label><input type="checkbox" v-model="pipe" /> pipe</label>
  <label><input type="checkbox" v-model="muku" /> muku</label>
  <button class="but" @click="send">推論</button>
  <br />
  <canvas
    ref="canvas"
    @mousedown="mouseDown"
    @mouseup="mouseUp"
  ></canvas>
</template>

<script setup>
import { ref } from "vue"

const imageFile = ref(null)
const canvas = ref(null)
const ctx = ref(null)

const imgObj = ref(null)
const scale = ref(1)

const start = ref(null)
const roi = ref(null)

const pipe = ref(true)
const muku = ref(true)

const MAX_SIZE = 1400

// --------------------
// 画像読み込み
// --------------------
const onFile = e => {
  imageFile.value = e.target.files[0]
  // ★ ROIをリセット
  roi.value = null
  start.value = null

  imgObj.value = new Image()
  imgObj.value.onload = () => {
    const w = imgObj.value.width
    const h = imgObj.value.height

    scale.value = Math.min(MAX_SIZE / w, MAX_SIZE / h, 1)

    canvas.value.width = Math.round(w * scale.value)
    canvas.value.height = Math.round(h * scale.value)

    ctx.value = canvas.value.getContext("2d")
    ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)
    ctx.value.drawImage(
      imgObj.value,
      0,
      0,
      canvas.value.width,
      canvas.value.height
    )
  }

  imgObj.value.src = URL.createObjectURL(imageFile.value)
}

// --------------------
// ROI選択
// --------------------
const mouseDown = e => {
  start.value = { x: e.offsetX, y: e.offsetY }
}

const mouseUp = e => {
  if (!start.value) return

  roi.value = {
    x1: Math.min(start.value.x, e.offsetX),
    y1: Math.min(start.value.y, e.offsetY),
    x2: Math.max(start.value.x, e.offsetX),
    y2: Math.max(start.value.y, e.offsetY)
  }

  // 再描画
  ctx.value.drawImage(
    imgObj.value,
    0,
    0,
    canvas.value.width,
    canvas.value.height
  )

  ctx.value.strokeStyle = "lime"
  ctx.value.lineWidth = 2
  ctx.value.strokeRect(
    roi.value.x1,
    roi.value.y1,
    roi.value.x2 - roi.value.x1,
    roi.value.y2 - roi.value.y1
  )
}

// --------------------
// 推論送信
// --------------------
const send = async () => {
  if (!roi.value) {
    alert("ROIを選択してください")
    return
  }

  const fd = new FormData()
  fd.append("image", imageFile.value)

  // ★ 表示 → 元画像座標に戻す
  fd.append("x1", Math.round(roi.value.x1 / scale.value))
  fd.append("y1", Math.round(roi.value.y1 / scale.value))
  fd.append("x2", Math.round(roi.value.x2 / scale.value))
  fd.append("y2", Math.round(roi.value.y2 / scale.value))

  if (pipe.value) fd.append("classes[]", "pipe")
  if (muku.value) fd.append("classes[]", "muku")

  const res = await fetch("http://localhost:5000/predict", {
    method: "POST",
    body: fd
  })

  const blob = await res.blob()
  const img = new Image()

  img.onload = () => {
    canvas.value.width = img.width
    canvas.value.height = img.height
    ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)
    ctx.value.drawImage(img, 0, 0)
  }

  img.src = URL.createObjectURL(blob)
}
</script>

<style scoped>
.but {
  margin-left: 6px;
}
canvas {
  border: 1px solid #ccc;
  margin-top: 8px;
}
</style>
