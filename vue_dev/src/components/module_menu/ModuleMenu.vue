<script setup>
import ModuleMenuItems from './ModuleMenuItems.vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps(["selectedModule", "concepts", "selectedConcepts", "moduleItems"])
const emit = defineEmits(["updateSelectedModule", "updateSelectedNodes", "addModule", "openConceptModal"])


function moduleSelected(moduleId) {
    if (props.selectedModule.value === moduleId) {
        emit("updateSelectedModule", null)
    } else {

        emit("updateSelectedModule", moduleId)
    }
}
</script>

<template>
    <div class="module-menu-root">
        <div class="module-menu-header">
            <h2 class="roboto-bold">Modules</h2>
            <hr style="width: 100%; border-color: var(--gold-line-color);"/>
            <img 
                src="/aspire/static/assets/icon-add.png" 
                title="Add New Module"
                @click="emit('addModule')"
                />
        </div>
        <span 
            class="module-accordion-container"
            >
            <ModuleMenuItems 
                v-for="item in props.moduleItems.filter(collection => collection.type === 'module')"
                :key="item.id"
                :module="item"
                :concepts="Object.values(props.concepts).filter(concept => concept.module.includes(item.id))"
                :selected-concepts="props.selectedConcepts"
                :selected-module="props.selectedModule"
                :update-selected-module="moduleSelected"
                @update-selected-nodes="value => emit('updateSelectedNodes', 'update', value)"
                @open-concept-modal="() => emit('openConceptModal')"
            />
        </span>

    </div>
</template>

<style scoped>
h3 {
    margin-top: 8px;
    margin-bottom: 0;
    height: 2rem;
    color: var(--core-primary);
}

.module-menu-root {
    height: 100%;
    width: 100%;
    margin-left: 0.5rem;
    padding-bottom: 0.5rem;
}

.module-menu-header{
    height: 4%;
    position: relative;
}
.module-accordion-container {
    display: block;
    width: 100%;
    height: 92%;
    overflow-y: scroll;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: var(--accent-primary) var(--bg-color);
    margin-top: .25rem;
    margin-right: .25rem;
}


.module-menu-header > img {
    position: absolute;
    right: 1rem;
    top: 0;
    aspect-ratio: 1/1;
    height: 2rem;
}
.module-menu-header > img:hover {
    height: 2.1rem;
}
.module-menu-header > img:active {
    /* background-color: var(--gold-line-color);
    border-radius: 50%; */
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}

</style>