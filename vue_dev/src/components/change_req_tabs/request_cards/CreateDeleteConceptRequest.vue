<script setup>
/* eslint-disable */
import { ref, defineProps, defineModel, computed, reactive, defineEmits } from 'vue';
import * as vNG from "v-network-graph"

const props = defineProps(['isExpanded', 'updateParams'])

const changeRequest = defineModel('changeRequest')

const nodes = {'concept': {'name': props.changeRequest.entity_data.name}}
const configs = {
    view: {
        panEnabled: false,
        zoomEnabled: false,
    },
    node: {
        draggable: false,
        selectable: false,
        normal: {
            radius: 24,
        },
        label: {
            direction: 'north',
            fontSize: 14 
        }
    },
}

</script>

<template>
    <div class="card-content">
        <v-network-graph 
            ref="graph" 
            :nodes="nodes" 
            :configs="configs"
            class="concept-graph"

        />
        <hr />
        <div v-if="updateParams.id !== changeRequest.id">
            <p><strong>Name:</strong> {{ changeRequest.entity_data.name }}</p>
            <p><strong>Subject:</strong> {{ changeRequest.entity_data.subject }}</p>
            <p><strong>Difficulty:</strong> {{ changeRequest.entity_data.difficulty }}</p>
            <p><strong>Summary:</strong> {{ changeRequest.entity_data.summary }}</p>
        </div>
        <div 
            v-if="updateParams.id === changeRequest.id"
            class="update-area"
        >
            <p><strong>Name:</strong> <input v-model="changeRequest.entity_data.name"/></p>
            <p><strong>Subject:</strong> <input v-model="changeRequest.entity_data.subject"/></p>
            <p><strong>Difficulty:</strong> <input v-model="changeRequest.entity_data.difficulty"/></p>
            <p><strong>Summary:</strong></p>
            <textarea v-model="changeRequest.entity_data.summary"/>
        </div>
    </div>

</template>

<style scoped>
.card-content {
    height: 100%;
}
.concept-graph {
    height: 30%;
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