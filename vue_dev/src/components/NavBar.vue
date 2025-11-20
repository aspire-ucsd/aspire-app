<script setup>
import { getCurrentInstance, ref, watch, defineProps, inject, defineEmits } from 'vue';
import NavBtn from "./NavBtn.vue";

// Define props
const props = defineProps({
  isCollapsed: Boolean
});

// Define emits
const emit = defineEmits(['toggle-collapse']);

const currentTab = inject("currentTab");

// Get the current instance and components
const tabs = Object.values(getCurrentInstance().appContext.components).filter(comp => comp.name && comp.name !== "apexchart");
// console.log(tabs)
// State for controlling the collapsed state of the navbar
const isCollapsed = ref(true);

// Watch for prop changes to animate the navbar
watch(() => props.isCollapsed, (newVal) => {
  isCollapsed.value = newVal;
});

const updateTab = (tabName) => {
  currentTab.value = tabName;
};

// Toggle collapse state
const toggleCollapse = () => {
  emit('toggle-collapse');
};
</script>

<template>
  <div class="nav-container" :class="{ collapsed: isCollapsed }">
    <div class="tabs-container">
      <!-- Aspire Logo or Text -->
      <div class="nav-btn logo-btn">
        <template v-if="isCollapsed">
          <img 
            src="/aspire/static/assets/aspire_new.png"
            class="nav-btn-icon collapsed-logo" 
            alt="Aspire Logo"
          />
        </template>
        <template v-else>
          <span class="aspire-text">ASPIRE</span>
        </template>
      </div>
      <!-- Other Tabs -->
      <div class="nav-btn" v-for="tab in tabs" :key="tab.name" @click="updateTab(tab.name)">
        <NavBtn :tab="tab" />
        <span v-if="!isCollapsed">{{ tab.friendly_name }}</span>
      </div>
    </div>
    <!-- Toggle Button -->
    <button @click="toggleCollapse" class="collapse-button" :class="{ 'collapsed': isCollapsed }">
      <img :src="isCollapsed ? '/aspire/static/assets/icon-SideBar.png' : '/aspire/static/assets/icon-SideBar.png'" />
    </button>
  </div>
</template>

<style scoped>
@keyframes slideInNav {
  from {
    width: 50px;
  }
  to {
    width: 200px; /* Adjust the width as needed */
  }
}

@keyframes slideOutNav {
  from {
    width: 200px; /* Adjust the width as needed */
  }
  to {
    width: 50px;
  }
}

.nav-container {
  width: 200px; /* Set the expanded width */
  height: 90vh; /* Set the height to 100vh to take up the entire viewport height */
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #13294B;
  transition: width 1s ease-out, background-color 0.3s;
  position: fixed; /* Ensure positioning context for the toggle button */
  animation: slideInNav 1s ease-out forwards;
  top: 5vh;
  left: 0;
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
}

.nav-container.collapsed {
  width: 50px; /* Set the collapsed width */
  animation: slideOutNav 1s ease-out forwards;
}

.tabs-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center; /* Align items to the center */
  flex-grow: 1; /* Ensure it takes the remaining space */
  justify-content: space-between; /* Spread out the icons evenly */
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center; /* Center the icons horizontally */
  padding: 0.5rem;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%; /* Ensure the button takes up the full width */
}

.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-btn-icon {
  border-radius: .5rem;
  width: 36px;
  height: 36px;
  aspect-ratio: 1/1;
  text-align: center;
  padding: 0;
  color: #C69214;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: .5rem;
  margin-bottom: .5rem;
  position: relative; /* Position relative to enable positioning of pseudo-element */
}

.btn-active {
  background-color: #182B49;
}

.btn-active::after {
  content: "";
  position: absolute;
  bottom: -10px; /* Position the triangle at the bottom */
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid #FFFF; /* Same color as the active background */
}

.nav-btn-icon:hover {
  box-shadow: 2px 2px 4px 4px #C69214;
}

.nav-btn-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.collapsed-logo {
  width: 36px;
  height: 36px;
}

.aspire-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #FFFFFF;
  margin-left: 1rem;
}

span {
  display: inline-block;
  margin-left: 1rem;
}

/* Added styles for the collapse button */
.collapse-button {
  background: none;
  border: none;
  cursor: pointer;
  margin-bottom: 10px; /* Add some space at the bottom */
  transition: left 1s ease-out;
  z-index: 1;
}

.collapse-button img {
  width: 24px;
  height: 24px;
}
</style>