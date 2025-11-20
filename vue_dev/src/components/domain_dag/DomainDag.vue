<script>
export default {
    name: 'DomainDag',
    friendly_name: "Domain Editor",
    icon: "/static/assets/icon-DomainEditor.png",
}
</script>
<script setup>
import { ref, toRef, reactive, defineProps, watch } from 'vue';
import * as vNG from "v-network-graph"
// import dagre from "dagre/dist/dagre.min.js"
import DomainZoomSlider from "@/components/domain_dag/DomainZoomSlider.vue";



const props = defineProps([
    "nodes",
    "edges",
    "selectedNodes",
    "focusNode",
    "defaultSettings",
    "selectedModule",
    "selectedEdges",
    "getColor",
    "graphHandler"
])

const zoomLevel = ref(1)

const layouts = reactive({
    nodes: {},
})




// function getEdgeColor(edge) {
//     if (props.selectedEdges.includes(`edge|${edge.source}|${edge.target}`)) {
//         return "#dd8800"
//     } else {
//         return "#aaa"
//     }
// }

class minLayout {
    onDeactivate = () => null

    activate(parameters) {
        const { nodePositions, nodes, configs, emitter, scale, svgPanZoom } = parameters
        const onDrag = (positions) => {
            for (const [id, pos] of Object.entries(positions)) {
                const layout = this.getOrCreateNodePosition(nodePositions, id)
                this.setNodePosition(layout, pos)
            }
        }

        emitter.on("node:dragstart", onDrag)
        emitter.on("node:pointermove", onDrag)
        emitter.on("node:dragend", onDrag)

        this.onDeactivate = () => {
            emitter.off("node:dragstart", onDrag)
            emitter.off("node:pointermove", onDrag)
            emitter.off("node:dragend", onDrag)
        }
    }

    deactivate() {
        if (this.onDeactivate) {
            this.onDeactivate()
        }
    }

    setNodePosition(nodeLayout, pos) {
        nodeLayout.value.x = Math.round(pos.x, 3)
        nodeLayout.value.y = Math.round(pos.y, 3)
    }

    getOrCreateNodePosition(nodePositions, node) {
        const layout = toRef(nodePositions.value, node)
        if (!layout.value) {
            layout.value = { x: 0, y: 0 }
        }
        return layout
    }
}

function labelOverflow(node) {
    if (props.graphHandler.nodeHovered.value === node.id || props.selectedNodes.includes(node.id)) {
        return node.name
    }
    else if (node.name.length > 18) {
        return node.name.slice(0, 15) + '...'
    } else {
        return node.name
    }
}

function compileConfig() {
    let config = {
        view: {
            autoPanAndZoomOnLoad: "fit-content",
            minZoomLevel: 0.1,
            maxZoomLevel: 3,
            onBeforeInitialDisplay: () => props.graphHandler.layout(),
            layoutHandler: new minLayout()
        },
        node: {
            selectable: props.defaultSettings.selectable,
            normal: {
                type: "circle",
                radius: _ => (props.graphHandler.layoutConfig.value.nodeSize / 2) * zoomLevel.value,
                strokeWidth: 0,
                strokeColor: "#000000",
                strokeDasharray: "0",
                color: node => props.getColor(node)
            },
            label: {
                direction: "north",
                color: props.defaultSettings.textColor,
                fontSize: _ => 12 * zoomLevel.value,
                fontFamily: "Roboto",
                margin: 4,
                text: node => labelOverflow(node),
                background: {
                    visible: true,
                    color: "#ffffff",
                    padding: 0,
                    borderRadius: 5
                }
            },
            zOrder: {
                enabled: true,
                zIndex: 0,
                bringToFrontOnHover: true,   
                bringToFrontOnSelected: true, 
                }
        },
        edge: {
            selectable: props.defaultSettings.selectable,
            normal: {
                color: edge => props.getColor(edge, 'edge'),
                width: _ => 3 * zoomLevel.value,
            },
            selected: {
                width: 3,
                color: "#dd8800",
                dasharray: "0",
                linecap: "round",
            },
            margin: 12,
            marker: {
                target: {
                    type: "arrow",
                    width: 4,
                    height: 4,
                }
            }
        }
    }

    if (props.defaultSettings.selectable) {
        config.node.selected = {
            type: "circle",
            radius: _ => (props.graphHandler.layoutConfig.value.nodeSize) * zoomLevel.value,
            strokeWidth: 0,
            strokeColor: "#000000",
            strokeDasharray: "0",
            color: node => props.getColor(node)
        }
    }
    if (props.defaultSettings.hoverable){
        config.node.hover = {
            type: "circle",
            radius: _ => (props.graphHandler.layoutConfig.value.nodeSize / 2) * zoomLevel.value + 8,
            strokeWidth: 0,
            strokeColor: "#000000",
            strokeDasharray: "0",
            color: node => props.getColor(node)
        }
    }
    if (props.defaultSettings.focusRing) {
        config.node.focusring = {
            width: 4,
            padding: 3,
            dasharray: "0",
            color: "#000000"
        }
    }
        // config.node.label.color = node => (
        //     props.selectedNodes.includes(node.id) && !(props.focusNode === node.id)
        //         ?
        //         "#fffff"
        //         :
        //         props.defaultSettings.textColor
        // )
        // config.node.label.background = node => getColor(node, "label")
    return config
}



const configs = reactive(vNG.defineConfigs(compileConfig()))

const graph = ref(vNG.VNetworkGraphInstance)

function updateLayout() {
    graph.value?.transitionWhile(() => {
        props.graphHandler.layout()
    })
    graph.value.panToCenter()
}

watch(props.graphHandler.layoutConfig.value, () => {
    updateLayout()
})

function startBoxSelection() {
    graph.value?.startBoxSelection({
        stop: "pointerup", // Trigger to exit box-selection mode
        type: "append", // Behavior when a node is within a selection rectangle
        withShiftKey: "invert", // `type` value if the shift key is pressed
    })
}

function stopBoxSelection() {
    graph.value?.stopBoxSelection()
}

const eventHandlers = {
    "*": (type, event) => {
        props.graphHandler.eventRouter(type, event)
    }
}

function snapToSelectedNodes(){
    let coords = []
    for (let selected of props.selectedNodes) {
        const target_position = layouts.nodes[selected]
        coords.push([target_position.x, target_position.y])
    }

    const total = coords.length

    const sum = coords.reduce((acc, coord) => {
        acc.x += coord[0];
        acc.y += coord[1];
        return acc;
    }, { x: 0, y: 0 });

    // Calculate the average x and y coordinates
    const centerX = sum.x / total;
    const centerY = sum.y / total;

    graph.value.panTo(graph.value.translateFromSvgToDomCoordinates({x: centerX, y: centerY}))

}
console.log(props.graphHandler.layouts)
</script>

<template>
    <div class="graph-box">
        <v-network-graph 
            ref="graph" 
            :nodes="props.nodes" 
            :edges="props.edges" 
            :layouts="props.graphHandler.layouts" 
            :configs="configs"
            :event-handlers="eventHandlers" 
            v-model:zoom-level="zoomLevel"

        />
        <DomainZoomSlider class="zoom-slider" v-model:zoom-level="zoomLevel" />
        <slot 
            :boxSelect="props.graphHandler.isBoxSelectionMode.value ? stopBoxSelection : startBoxSelection" 
            :updateLayout="updateLayout"
            :snapToSelectedNodes="snapToSelectedNodes"
            >

        </slot>
    </div>
</template>

<style>

.zoom-slider{
    position: absolute;
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

.graph-box {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-color: var(--bg-color);
    box-shadow: 1px 1px 2px 0px rgb(169, 169, 169);
    border-radius: 8px;
    text-transform: capitalize;
}

.options-menu {
    display: flex;
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
</style>
