<template>
  <div class="shell">
    <nav class="nav">
      <router-link to="/domains">Domains</router-link>
      <router-link to="/search">Search</router-link>
      <router-link to="/ingestion">Ingestion</router-link>
      <router-link to="/admin">Admin</router-link>
    </nav>
    <main class="main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Inter, system-ui, sans-serif; background: #F5F5F7; }
.shell { display: flex; min-height: 100vh; }
.nav { width: 200px; background: #fff; padding: 20px; border-right: 1px solid #e5e5e7; }
.nav a { display: block; padding: 12px 16px; color: #333; text-decoration: none; border-radius: 8px; margin-bottom: 4px; }
.nav a:hover { background: #f0f0f2; }
.main { flex: 1; padding: 24px; }
</style>