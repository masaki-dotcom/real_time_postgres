<template>
  <div class="p-4 grid grid-cols-3 gap-4">

    <!-- ① ユーザー一覧 -->
    <div>
      <h2 class="font-bold mb-2">ユーザー一覧</h2>
      <client-only>
        <ul>
          <li v-for="u in users" :key="u.id"
              class="cursor-pointer hover:bg-gray-100 p-1"
              @click="loadUserDetail(u.id)">
            {{ u.id }} : {{ u.name }} - {{ u.email }}
          </li>
        </ul>
      </client-only>
    </div>

    <!-- ② 閲覧エリア -->
    <div>
      <h2 class="font-bold mb-2">閲覧</h2>
      <div v-if="selectedUser">
        <p>ID: {{ selectedUser.id }}</p>
        <p>名前: {{ selectedUser.name }}</p>
        <p>メール: {{ selectedUser.email }}</p>
      </div>
      <p v-else>左の一覧から選択してください。</p>
    </div>

    <!-- ③ 新規作成・編集 -->
    <div>
      <h2 class="font-bold mb-2">新規作成</h2>
      <input v-model="newUser.name" placeholder="名前" class="border p-1 w-full mb-2" />
      <input v-model="newUser.email" placeholder="メール" class="border p-1 w-full mb-2" />
      <button @click="createUser" class="bg-blue-500 text-white px-2 py-1 rounded">作成</button>

      <div class="mt-8">
        <h2 class="font-bold mb-2">編集</h2>
        <div v-if="editUser.id">
          <input v-model="editUser.name" placeholder="名前" class="border p-1 w-full mb-2" />
          <input v-model="editUser.email" placeholder="メール" class="border p-1 w-full mb-2" />
          <button @click="updateUser" class="bg-green-500 text-white px-2 py-1 rounded">更新</button>
        </div>
        <p v-else>左でユーザーを選択してください。</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { ref, watch, onMounted } from 'vue'
import { useUserEvents } from '~/composables/useUserEvents'

const users = ref<any[]>([])
const selectedUser = ref<any>(null)

// 新規作成用
const newUser = ref({ name: '', email: '' })

// 編集用
const editUser = ref({ id: null, name: '', email: '' })

// 全ユーザー取得
async function loadUsers() {
  try {
    const res = await axios.get('http://localhost:5001/users')
    users.value = res.data
    console.log('📄 loadUsers:', users.value)
  } catch (e) {
    console.error('loadUsers error', e)
  }
}

// ユーザー詳細取得
async function loadUserDetail(id: number) {
  try {
    const res = await axios.get(`http://localhost:5001/users/${id}`)
    selectedUser.value = res.data
    editUser.value = { ...res.data } // 編集フォームにコピー
    console.log('📄 loadUserDetail:', selectedUser.value)
  } catch (e) {
    console.error('loadUserDetail error', e)
  }
}

// 新規作成
async function createUser() {
  try {
    await axios.post('http://localhost:5001/users', newUser.value)
    console.log('➕ createUser success:', newUser.value)
    newUser.value = { name: '', email: '' }
  } catch (e) {
    console.error('createUser error', e)
  }
}

// 編集保存
async function updateUser() {
  try {
    await axios.put(`http://localhost:5001/users/${editUser.value.id}`, editUser.value)
    console.log('✏️ updateUser success:', editUser.value)

    // ここで強制的に詳細更新
    await loadUserDetail(editUser.value.id)
    // 必要ならユーザー一覧も更新
    await loadUsers()
  } catch (e) {
    console.error('updateUser error', e)
  }
}

// 初期ロード
onMounted(() => {
  console.log('🟢 onMounted loadUsers')
  loadUsers()
})

// SSE リアルタイム更新
const { lastEvent } = useUserEvents()

watch(lastEvent, (ev) => {
  console.log('test:')

  if (!ev) return
  console.log('🔔 SSE Watch triggered:', ev)

  // ユーザー一覧更新
  loadUsers()

  // 選択中ユーザーが通知対象なら詳細も更新  
  if (selectedUser.value?.id === ev.id) {
    loadUserDetail(ev.id)
    console.log('Selected user updated via SSE:', selectedUser.value)
  }
}, { deep: true })
</script>
