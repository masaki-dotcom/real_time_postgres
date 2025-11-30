<script setup>
definePageMeta({
  ssr: false   // これがないと hydration mismatch が発生する
})

import { ref, onMounted } from "vue"

const emails = ref([])
const name = ref("")
const email = ref("")
const editingId = ref(null)

const apiBase = "http://localhost:5000"

// -------------------------------
// 初期データ読み込み
// -------------------------------
const loadData = async () => {
  const res = await $fetch(`${apiBase}/emails`)
  emails.value = res
}

// -------------------------------
// 新規登録
// -------------------------------
const addEmail = async () => {
  if (!name.value || !email.value) return alert("名前とメールを入れてね")

  await $fetch(`${apiBase}/emails`, {
    method: "POST",
    body: {
      name: name.value,
      email: email.value,
    },
  })

  name.value = ""
  email.value = ""
}

// -------------------------------
// 編集開始
// -------------------------------
const startEdit = (item) => {
  editingId.value = item.id
  name.value = item.name
  email.value = item.email
}

// -------------------------------
// 更新処理
// -------------------------------
const updateEmail = async () => {
  if (!editingId.value) return

  await $fetch(`${apiBase}/emails/${editingId.value}`, {
    method: "PUT",
    body: {
      name: name.value,
      email: email.value,
    },
  })

  editingId.value = null
  name.value = ""
  email.value = ""
}

// -------------------------------
// SSE リアルタイム反映
// -------------------------------
onMounted(() => {
  loadData()

  const stream = new EventSource(`${apiBase}/emails/stream`)

  stream.onmessage = (event) => {
    emails.value = JSON.parse(event.data)
  }
})
</script>

<template>
  <div class="p-5">
    <h1 class="text-2xl font-bold mb-4">リアルタイム Email 管理</h1>

    <!-- 入力フォーム -->
    <div class="border p-4 rounded mb-6">
      <input
        v-model="name"
        placeholder="名前"
        class="border p-2 mr-2"
        type="text"
      />
      <input
        v-model="email"
        placeholder="メール"
        class="border p-2 mr-2"
        type="email"
      />

      <button
        v-if="!editingId"
        @click="addEmail"
        class="bg-blue-500 text-white px-4 py-2 rounded"
      >
        追加
      </button>

      <button
        v-else
        @click="updateEmail"
        class="bg-green-500 text-white px-4 py-2 rounded"
      >
        更新
      </button>
    </div>

    <!-- 一覧表示 -->
    <table class="w-full border">
      <thead>
        <tr class="bg-gray-200">
          <th class="border p-2">ID</th>
          <th class="border p-2">名前</th>
          <th class="border p-2">メール</th>
          <th class="border p-2">操作</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="item in emails" :key="item.id">
          <td class="border p-2">{{ item.id }}</td>
          <td class="border p-2">{{ item.name }}</td>
          <td class="border p-2">{{ item.email }}</td>
          <td class="border p-2 text-center">
            <button
              @click="startEdit(item)"
              class="bg-yellow-400 text-black px-3 py-1 rounded"
            >
              編集
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
