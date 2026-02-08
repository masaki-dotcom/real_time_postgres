<template>
  <input type="file" @change="onFile" />
  <label><input type="checkbox" v-model="Box" /> Box</label>
  <label><input type="checkbox" v-model="Label" /> Label</label>
  <button class="but" @click="send">推論</button>

  <div style="margin-top:8px">
    pipe: {{ counts.pipe }}　
    muku: {{ counts.muku }}
  </div>

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

const Box = ref(true)
const Label = ref(true)

const counts = ref({ pipe: 0, muku: 0 })

const MAX_SIZE = 1400

// --------------------
// 画像読み込み
// --------------------
const onFile = e => {
  imageFile.value = e.target.files[0]
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
    ctx.value.drawImage(imgObj.value, 0, 0, canvas.value.width, canvas.value.height)
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

  ctx.value.drawImage(imgObj.value, 0, 0, canvas.value.width, canvas.value.height)

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

  const sendRoi = {
    x1: Math.round(roi.value.x1 / scale.value),
    y1: Math.round(roi.value.y1 / scale.value),
    x2: Math.round(roi.value.x2 / scale.value),
    y2: Math.round(roi.value.y2 / scale.value)
  }

  const fd = new FormData()
  fd.append("image", imageFile.value)
  fd.append("x1", sendRoi.x1)
  fd.append("y1", sendRoi.y1)
  fd.append("x2", sendRoi.x2)
  fd.append("y2", sendRoi.y2)

  if (Box.value) fd.append("classes[]", "Box")
  if (Label.value) fd.append("classes[]", "Label")

  const res = await fetch("http://localhost:5000/predict", {
    method: "POST",
    body: fd
  })

  const data = await res.json()

  // 🔢 cls個数
  counts.value.pipe = data.counts.pipe ?? 0
  counts.value.muku = data.counts.muku ?? 0

  // 🖼 base64画像描画
  const img = new Image()
  img.onload = () => {
    canvas.value.width = img.width
    canvas.value.height = img.height
    ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)
    ctx.value.drawImage(img, 0, 0)
  }

  img.src = "data:image/jpeg;base64," + data.image
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
