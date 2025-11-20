<script setup>
import { inject } from 'vue';

const props = defineProps(["tab"]);
const currentTab = inject("currentTab");

const updateTab = () => {
  currentTab.value = props.tab.name;
};
</script>

<template>
  <div @click="updateTab" class="nav-btn-wrapper">
    <img 
        class="nav-btn-icon" 
        :class="{'btn-active': currentTab.value === props.tab.name}" 
        :src="props.tab.icon" 
        :title="props.tab.friendly_name"
    />
  </div>
</template>

<style scoped>
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
    /* box-shadow: 2px 2px 4px 4px #C69214; */
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}

.nav-btn-wrapper {
    display: flex;
    align-items: center;
    cursor: pointer;
}
</style>