<script>
export default {
    name: 'StudentModel',
    view: 'student',
    friendly_name: "Course Progress",
    icon: "/aspire/static/assets/icon-DomainEditor.png",
    props: {
        msg: String
    }
}
</script>

<script setup>
import DomainDag from "../components/domain_dag/DomainDag.vue"
import DomainDagUtilities from "../utils/DagUtils.js"
import LoadingWheel from "@/components/LoadingWheel.vue";
import ConceptSearch from '@/components/domain_dag/ConceptSearch.vue'

import axios from "axios";
import { onBeforeMount } from "vue"

const tool_domain = window.contextData.tool_domain

let dagUtil = new DomainDagUtilities()

onBeforeMount(async () => {
    axios.get(`${tool_domain}/module/course`).then((response) => {
        let moduleItems = Object.values(response.data)

        let moduleIds = moduleItems.map(item => item.module_id)
        console.log(moduleIds)
        if (moduleIds.length > 0) {
            const params = new URLSearchParams()
            params.append("list_of_ids", moduleIds.join(","))

            axios.get(`${tool_domain}/concept/from_modules`, { params }).then((response) => {
                let nodes = response.data
                const conceptParams = new URLSearchParams()
                conceptParams.append("list_of_names", Object.keys(nodes).join("|"))

                axios.get(`${tool_domain}/concept/cc/many`, { "params": conceptParams }).then((response) => {
                    let edges = response.data
                    axios.get(`${tool_domain}/student/model/course`, { "params": conceptParams }).then((response) => {
                        console.log(response.data, nodes)
                        response.data.forEach(score => {
                            if (nodes[score.concept_name]) {
                                nodes[score.concept_name].params = { score: score.score, changeHistory: score.change_history }
                            }
                        })
                        console.log(nodes)
                        dagUtil.initialize(nodes, edges)
                    })

                })
            })
        }
    })
})

const defaultSettings = {
    nodeColor: "#00629B",
    focusColor: "#ffdd00",
    moduleColor: "#FC8900",
    edgeColor: "",
    textColor: "#00000",
    nodeSize: 30,
    selectable: false,
    hoverable: true,
    focusRing: false
}


function scoreToColor(value) {
    value = Math.max(0, Math.min(1, value))

    let red, green

    if (value <= 0.5) {
        red = 220
        green = Math.round(255 * (value / 0.5))

    } else {
        green = 220
        red = Math.round(255 * ((1 - value) / 0.5))
    }

    const redHex = red.toString(16).padStart(2, '0')
    const greenHex = green.toString(16).padStart(2, '0')

    return `#${redHex}${greenHex}00`;
}

function getColor(node, mode = "node") {
    let color = defaultSettings.nodeColor
    if (node.params.score) {
        color = scoreToColor(node.params.score)
    }
    if (mode === "label")
        return {
            visible: true,
            color: color,
            padding: 2,
            borderRadius: 5
        }
    else {
        return color
    }
}

function onNodeClick(node) {
    dagUtil.focusNode.value = node.node
}

function onBgClick(event) {
    dagUtil.focusNode.value = null
}

function getChartData() {
    let node = dagUtil.nodes.value[dagUtil.focusNode.value]
    let changeHistory = node.params.changeHistory
    if (changeHistory) {
        let series = changeHistory.map((change) => {
            let date = Date.parse(change.timestamp)
            return {x: new Date(date), y: Number(change.score).toFixed(2)}
        })
        return [{name: dagUtil.focusNode.value, data: series}]
    } else {
        return [{name: dagUtil.focusNode.value, data: []}]
    }
}

function getChartOptions() {
    const chartOptions = {
        legend: {
            show: true,
            position: 'bottom'
        },
        chart: {
            type: 'area',
            stacked: false,
            height: 350,
            zoom: {
                type: 'x',
                enabled: true,
                autoScaleYaxis: true
            },
            toolbar: {
                autoSelected: 'zoom'
            }
        },
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 0,
        },
        title: {
            text: dagUtil.focusNode.value,
            offsetY: 16,
            align: 'left'
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                inverseColors: false,
                opacityFrom: 0.5,
                opacityTo: 0,
                stops: [0, 90, 100]
            },
        },
        yaxis: {
            max: 1.0,
            min: 0.0,
            title: {
                text: 'Score'
            },
        },
        xaxis: {
            type: 'datetime',
            title: {
                text: 'Time'
            },
        },
        tooltip: {
            shared: false,
            // y: {
            //     formatter: function (val) {
            //         return (val / 1000000).toFixed(0)
            //     }
            // }
        }
    }
    return chartOptions
}




</script>
<template>
    <div class="domain-editor" v-if="dagUtil.is_initialized.value">
        <DomainDag 
            :nodes="dagUtil.nodes.value" 
            :edges="dagUtil.edges.value" 
            :focus-node="dagUtil.focusNode.value"
            :selectedNodes="dagUtil.selectedNodes.value" 
            :selectedModule="dagUtil.selectedModule.value"
            :defaultSettings="defaultSettings" 
            :selected-edges="dagUtil.selectedEdges.value" 
            :getColor="getColor"
            @onNodeClick="onNodeClick"
            @onBgClick="onBgClick"
        >
            <template #default="{ updateLayout, snapToSelectedNodes }">
                <div class="menu-wheel">
                </div>
                <div class="options-menu">
                    <img title="Refresh Layout" aria-label="Refresh Layout" class="refresh-btn-icon"
                        src="/static/assets/loading-icon.png" @click="updateLayout('BT')" />
                </div>
                <div class="display-options">
                    <ConceptSearch @updateSelectedNodes="dagUtil.updateSelectedNodes" :concepts="dagUtil.nodes.value"
                        :selected-concepts="dagUtil.selectedNodes.value" :snapToSelectedNodes="snapToSelectedNodes" />
                </div>
                <div class="student-model-analytics" v-if="dagUtil.focusNode.value">
                    <apexchart type="area" :options="getChartOptions()" :series="getChartData()"></apexchart>
                </div>
            </template>
        </DomainDag>
    </div>
    <div class="domain-editor" v-else>
        <LoadingWheel :loading-text="'Loading...'" />
    </div>
</template>

<style scoped>
.domain-editor {
    display: flex;
    flex-direction: row;
    height: 100% !important;
    width: 100%;
    min-height: 100% !important;
}

.graph {
    height: 100%;
    position: relative;
    top: 0;
    left: 0;
}

.display-options {
    position: absolute;
    display: flex;
    flex-direction: column;
    top: 3rem;
    left: 6px;
    z-index: 999;
    width: 12rem;

}

.options-menu {
    position: absolute;
    display: flex;
    top: 6px;
    left: calc(6px + 10rem);
    z-index: 999;
    flex-direction: row;
    align-items: center;
    justify-content: center;
}


.menu-wheel {
    position: absolute;
    display: flex;
    flex-direction: column;
    bottom: 6px;
    left: 6px;
    align-items: center;
    justify-content: center;
}

.refresh-btn-icon {
    border-radius: 50%;
    width: 2rem;
    aspect-ratio: 1/1;
    text-align: center;
    padding: 0;
    color: #C69214;
    margin: 1px;
    position: relative;
}

.refresh-btn-icon:hover {
    border: 1px solid #c6911400;
}

.refresh-btn-icon:active {
    border: 2px groove #C69214;
}

.student-model-analytics {
    position: absolute;
    top: 6px;
    right: 6px;
    /* height: 50%; */
    width: 25%;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0px 0px 2px black;
    padding: .5rem;
}
</style>