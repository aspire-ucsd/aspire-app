<script setup>
/* eslint-disable */
import { ref, defineProps, defineModel, computed, reactive, defineEmits } from 'vue';
import * as vNG from "v-network-graph"

const props = defineProps(['isExpanded', 'updateParams'])

const changeRequest = defineModel('changeRequest')
console.log(changeRequest.value)
const nodes = {
    'prereq_name': {'name': props.changeRequest.entity_data.prereq_name},
    'concept_name': {'name': props.changeRequest.entity_data.concept_name}
}
const edges = {
    'edge': {source: 'prereq_name', target: 'concept_name'}
}
const layouts = reactive({
    nodes: {
        'prereq_name': {x: 0, y: 85},
        'concept_name': {x: 0, y: 0},
    }
})
const configs = {
    view: {
        panEnabled: false,
        zoomEnabled: false,
    },
    node: {
        draggable: false,
        selectable: false,
        normal: {
            radius: 16,
        },
        label: {
            direction: 'north',
            fontSize: 14, 
            fontFamily: "Roboto",
            margin: 6,
            background: {
                    visible: true,
                    color: "#D9D9D9",
                    padding: 0.5,
                    borderRadius: 5
                }
        }
    },
    edge: {
            selectable: false,
            normal: {
                color: _ => changeRequest.value.modification_type === 'create' ? "#018c0d" : "#9C0000",
                width: 3,
            },
            margin: 4,
            marker: {
                target: {
                    type: "arrow",
                    width: 4,
                    height: 4,
                }
            }
        }
}

</script>

<template>
    <div class="card-content">
        <v-network-graph 
            ref="graph" 
            :nodes="nodes" 
            :edges="edges"
            :layouts="layouts"
            :configs="configs"
            class="concept-graph"

        />
        <hr />
    </div>

</template>

<style scoped>
.card-content {
    height: 100%;
}
.concept-graph {
    height: 100%;
}
.update-area {
    height: 70%;
}
.update-area > p {
    max-height: 15%;
}
.update-area > textarea {
    max-width: 100%;
    min-width: 100%;
    width: 100%;
    min-height: 40%;
    max-height: 40%;
}
</style>