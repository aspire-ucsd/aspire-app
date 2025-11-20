<script setup>
import { defineProps, defineEmits, ref, watch, nextTick } from 'vue';
import { ListboxContent, ListboxItem, ListboxItemIndicator, ListboxRoot } from 'radix-vue'

const emit = defineEmits(["updateSelectedNodes", "openConceptModal"])
const props = defineProps(["module", "concepts", 'selectedConcepts', 'selectedModule', 'updateSelectedModule'])

const selectedConcepts = ref([])
const contentHeight = ref(0);
const content = ref(null);

watch(props.selectedConcepts, (newVal) => {
    selectedConcepts.value.value = Object.values(newVal)
})

const toggleOpen = () => {
    props.updateSelectedModule(props.module.id)
    if (props.selectedModule.value === props.module.id) {
        nextTick(() => {
        contentHeight.value = content.value.scrollHeight;
        });
    } else {
        contentHeight.value = 0;
    }
};

</script>
<template>
    <div class="module-item-header" @click="toggleOpen">
        <h4>{{ props.module.label }}</h4>
        <img 
            src="/aspire/static/assets/icon-chevron.png"
            class="dropdown-btn-icon"
            :data-state="props.selectedModule.value === props.module.id"
        />
    </div>
    <div 
        class="module-item-contents"
        ref="content" 
        :data-state="props.selectedModule.value === props.module.id"
        :style="{'height': props.selectedModule.value === props.module.id ? `${contentHeight}px` : '0'}"
    
        >
        <p class="module-summary">{{ props.module.content_summary }}</p>
        <hr style="width: 100%; border-color: var(--gold-line-color);"/>
        <div class="module-header">
            <p class="roboto-bold">Concepts:</p>
            <img 
                class="ui-btn-icon" 
                src="/aspire/static/assets/icon-spark-gold.png"
                title="Generate Module Concepts"
                @click="() => emit('openConceptModal')"
            />
        </div>
        <ListboxRoot
            class="list-root"
            v-model="selectedConcepts.value"
            @update:model-value="(value) => emit('updateSelectedNodes', Object.values(value))"
            multiple
        >
            <ListboxContent
                class="concept-box"
            >
                <ListboxItem
                    v-for="concept in props.concepts"
                    :key="concept.id"
                    :value="concept.id"
                    class="concept-item"
                >
                    <span>{{concept.name}}</span>
                    <ListboxItemIndicator />
                </ListboxItem>
            </ListboxContent>
        </ListboxRoot>
    </div>
</template>
<style scoped>

.module-item-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    background-color: var(--core-primary);
    color: var(--gold-line-color);
    padding-left: .25rem;
}
.ui-btn-icon {
    height: 100%;
    aspect-ratio: 1/1;
    text-align: center;
    padding: 0;
    align-items: center;
    justify-content: center;
    margin: 1px;
    position: relative; 
}

.ui-btn-icon:hover {
    height: calc(100% - 3px);
}
.ui-btn-icon:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}
.dropdown-btn-icon {
    width: 10%;
    aspect-ratio: 1/1;
    text-align: center;
    padding: 0;
    display: fixed;
    align-items: center;
    justify-content: center;
    margin: 1px;
    position: relative; 
}


.dropdown-btn-icon[data-state="false"] {
    transform: rotate(180deg);
    transition: 300ms linear;
}

.dropdown-btn-icon[data-state="true"] {
    transform: rotate(0deg);
    transition: 300ms linear;
}
.module-item-contents {
    max-height: 60%;
    transition: height 0.3s ease;
}
.module-item-contents[data-state="false"]{
    overflow: hidden;
}

.module-item-contents[data-state="true"]{
    overflow-y: scroll;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: var(--accent-primary) var(--bg-color);
}


.module-summary{
    padding: .5rem;
}

p {
    margin: 0;
}
.module-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    height: 2rem;
    padding-bottom: 0.5rem;
}

.list-root {
    box-shadow: 1px 1px 5px -2px #000000;
}
.concept-box {
    display: flex;
    flex-direction: column;
}
.concept-item {
    user-select: none;
    border-bottom: 1px solid var(--gold-line-color);
    font-size: 1rem;
    color: var(--text-muted)
}
.concept-item:hover {
    font-weight: bold;
    color: var(--text-color)
}

.concept-item[data-state="checked"] {
    background-color: #7aff9e;
    font-weight: bold;
    color: var(--text-color)

}
</style>