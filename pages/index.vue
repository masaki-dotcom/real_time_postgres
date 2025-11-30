<template>
  <div>
    <h1>Emails</h1>
    <ul>
      <li v-for="email in emails" :key="email.id">
        {{ email.name }} - {{ email.email }}
      </li>
    </ul>

    <form @submit.prevent="addEmail">
      <input v-model="newName" placeholder="Name" />
      <input v-model="newEmail" placeholder="Email" />
      <button type="submit">Add</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const emails = ref<{id:number,name:string,email:string}[]>([])
const newName = ref("")
const newEmail = ref("")

onMounted(() => {
  const evtSource = new EventSource("http://localhost:5000/emails/stream")
  evtSource.onmessage = (event) => {
    emails.value = JSON.parse(event.data)
  }
})

async function addEmail() {
  await fetch("http://localhost:5000/emails", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newName.value, email: newEmail.value })
  })
  newName.value = ""
  newEmail.value = ""
}
</script>
