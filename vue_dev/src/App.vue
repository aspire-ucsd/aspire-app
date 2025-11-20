<script setup>
import NavBar from "./components/NavBar.vue";
import RegisterCourse from "./pages/RegisterCourse.vue"
import { getCurrentInstance, inject, ref } from "vue";
import "./styles/fonts.css"

const courseIsNew = ref(window.contextData.course_is_new)

const currentTab = inject("currentTab");
const tabs = getCurrentInstance().appContext.components;

const isDarkMode = ref(false);
const isCollapsed = ref(true);

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<template>
  <div v-if="!courseIsNew" id="app-main" :class="['main-container', { 'dark-mode': isDarkMode }]">
      <NavBar :isCollapsed="isCollapsed" @toggle-collapse="toggleCollapse" />
      <div class="main-content" :style="{ width: isCollapsed ? 'calc(100% - 50px)' : 'calc(100% - 200px)' }">
        <component :is="tabs[currentTab]"/>
      </div>
  </div>
  <RegisterCourse v-else/>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* .main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
} */

.dark-mode {
  --bg-color: #202123;
  --text-color: #ffffff;
  --banner-bg-color: #121212;
  --banner-text-color: #ffffff;
  --gold-line-color: #ffcc00;
  --box-shadow-light: rgba(255, 255, 255, 0.2);
  --box-shadow-dark: rgba(255, 255, 255, 0.6);
  --box-shadow-hover-light: rgba(255, 255, 255, 0.4);
  --box-shadow-hover-dark: rgba(255, 255, 255, 0.8);
}

.main-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content:flex-end;
  width: 100vw;
  height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow: hidden;
}

.dashboard {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
}

.main-content {
  padding: 10px;
  height: 100%;
  flex-direction: column !important;
  font-family: "Roboto", sans-serif;
  transition: width 1s ease-out;
}

.display-options {
    position: absolute;
    display: flex;
    flex-direction: column;
    top: 6px;
    left: 6px;
    z-index: 999;
    width: 10rem;
    
}
.popover-test {
    display: flex;
    width: fit-content;
    position: relative;
    left: calc(60px + var(width));
    top: 380px;
}
</style>