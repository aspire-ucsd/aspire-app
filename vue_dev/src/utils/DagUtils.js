import axios from "axios";
import { ref, reactive } from "vue";
import dagre from "dagre/dist/dagre.min.js"
/* eslint-disable */


export default class DomainDagUtilities {
    constructor() {

        this.nodes = ref({}) // Private - Must populate through the initialize() method
        this.edges = ref({}) // Private - Must populate through the initialize() method
        this.collections = ref([])

        this.changeRequestDrafts = ref({})
        this.focusNode = ref()
        this.nodeHovered = ref(null)
        this.selectedNodes = ref([])
        this.selectedEdges = ref([])
        this.selectedModule = ref()
        this.paramNodes = new Set([])

        this.layouts = reactive({
            nodes: {},
        })

        this.saving = ref(false)
        this.is_initialized = ref(false)
        this.isBoxSelectionMode = ref(false)

        this.styles = {
            focusColor: "#f55d42"
        }

        this.config = {
            "edge:select": this.onEdgeSelect,
            "node:pointerover": this.onNodeHover,
            "node:pointerout": this.onNodeHover,
            "node:select": this.onNodeSelect,
            "view:mode": this.onModeUpdate,
            "view:click": this.clearParams,
        }

        this.layoutConfig = ref({
            method: "default",
            nodeSize: 30,
            nodeSeparation: 2,
            rankSeparation: 2,
            groupScalingX: 1.25,
            groupScalingY: 2,
            direction: "BT",
            alignment: "",
            ranker: "tight-tree",
            acyclicer: 'greedy'
        })
        
        this.layoutMap = {
            "default": this.defaultLayout,
            "module-wise": this.moduleLayout
        }

        this.tool_domain = window.contextData.tool_domain
    }

    /**
     * Initializes the graph this class is mounted to with the desired nodes, edges, collections and configurations.
     * @category Init Method
     * @param {Object} nodes The nodes of the graph: 
    { 
        (nodeId): 
        {
            'name': (same as id), 
            'id': (nodeId - used internally by v-network-graph), 
            'module': [1, 2], 
            'params': {}, 
            'is_new': (bool) 
        } 
    }
     * @param {Object} edges The edges of the graph: 
    {
        'edge|source|target': 
        {
            'source': (source nodeId), 
            'target': (target nodeId)
        }
    }
     * @param {Array[Object]} collections The various collections nodes are grouped into: 
    [
        { 
            "label": "Test Module",
            "content_summary": "Introduction to docstrings",
            "type": "module",
            "order": (Integer),
            "course_id": 109,
            "id": 1
        }
    ]
     * @param {Object} configUpdate Object used to append or update this.config - Entries defined here override or expand behaviors resulting from graph events.
     * @param {Object} stylesUpdate Object used to append or update this.styles - Entries defined here override or expand style values of v-network-graph.
     */
    initialize = (
        nodes, 
        edges, 
        collections, 
        configUpdate, 
        stylesUpdate
    ) => {
        this.nodes.value = nodes
        this.edges.value = edges
        this.collections.value = collections
        this.config = {...this.config, ...configUpdate}
        this.styles = {...this.styles, ...stylesUpdate}
        this.is_initialized.value = true
    }



    /**
     * Centralized method for calling a layout function, uses the value set at this.layoutConfig.value.method as the key for selecting which layout callback to use
     * @category Callback Router
     */
    layout = () => {
        this.layoutMap[this.layoutConfig.value.method]?.call(this)
    }

    /**
     * Routes events emitted by v-network-graph to callbacks defined in this.config. 
     * All callbacks must accept 'type' and 'event' as an argument and will be called with the 'this' value associated with the class instance.
     * @category Callback Router
     * @param {String} type - The string name of the event emitted by v-network-graph, mapped to a callback defined in this.config.
     * @param {*} event - Event metadata, passed to all callbacks 
     */
    eventRouter = (type, event) => {
        this.config[type]?.call(this, type, event)
    }



    /**
     * Standard DAG layout algorithm with configurations for ranking, aligning, and spacing nodes.
     * @category Layout Method
     */
    defaultLayout = () => {
        if (Object.keys(this.nodes.value).length <= 1 || Object.keys(this.edges.value).length == 0) {
            return
        }

        const g = new dagre.graphlib.Graph()

        g.setGraph({
            align: this.layoutConfig.value.alignment,
            rankdir: this.layoutConfig.value.direction,
            nodesep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.nodeSeparation,
            edgesep: 0,
            ranksep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.rankSeparation,
            ranker: this.layoutConfig.value.ranker,
            acyclicer: this.layoutConfig.value.acyclicer
        })
        g.setDefaultEdgeLabel(() => ({}))
    
        Object.entries(this.nodes.value).forEach(([nodeId, node]) => {
            g.setNode(nodeId, { label: node.name, width: this.layoutConfig.value.nodeSize, height: this.layoutConfig.value.nodeSize })
        })
    
        Object.values(this.edges.value).forEach(edge => {
            if (!edge?.status || 'none' === 'delete') {

                g.setEdge(edge.source, edge.target)
            }
        })
        dagre.layout(g)
    
        g.nodes().forEach((nodeId) => {
            if (g.node(nodeId)) {
                const x = g.node(nodeId).x
                const y = g.node(nodeId).y
                this.layouts.nodes[nodeId] = { x, y }
            }
        })
    }
    /**
     * EXPERIMENTAL
     * 
     * Lays nodes out module-wise, 
     * 1) Gets all nodes belonging to each module.
     * 2) Lays each node group out at the graph origin using the default layout method.
     * 3) For each module group, stores the relative coordinates of the now layed out nodes and the group size.
     * 4) Identifies and stores the relationships/edges between modules based on their contained node relationships.
     * 5) Cleans up circular relationships by removing the edge with the lowest count of node junctions.
     * 6) Lays out each module as if it was a node using the previously identified module edges, uses the group size to determine spacing.
     * 7) The coordinates of each layed out module are used to perform a coordinate translation, this value becomes the new origin of the contained nodes.
     * 8) TODO: Nodes belonging to multiple modules need to have their new positions calculated relative to all their source modules
     * @category Layout Method
     */
    moduleLayout = () => {
        // Module-wise dag layout method, groups concepts by module, lays the concept groups out individually, 
        // creates a module layout using the sizes and edges of the group layout, translates the group layouts using the module position as new origin.
        // I'm sure this can be done so much more efficiently/cleaner, need to give it another pass to clean it up
        if (Object.keys(this.nodes.value).length <= 1 || Object.keys(this.edges.value).length == 0) {
            return
        }

        let moduleNodes = {}
        for (let module of Object.values(this.collections.value).filter(module => module.type === 'module')) {
            const nodeList = Object.values(this.nodes.value).filter(node => node.module.includes(module.id)).map(node => {
                return {name: node.id}
            })
            moduleNodes[module.id] = {name: module.label, concepts: nodeList, params: {}, id: module.id, module: []}
        }

        let edgeCounts = new Map();

        for (let edge of Object.values(this.edges.value)) {
            const targetModules = this.nodes.value[edge.target].module;
            const sourceModules = this.nodes.value[edge.source].module;

            for (let target of targetModules) {
                for (let source of sourceModules) {
                    if (source !== target) {
                        const edgeKey = `edge|${target}|${source}`;
                        const reverseKey = `edge|${source}|${target}`;

                        if (!edgeCounts.has(edgeKey)) edgeCounts.set(edgeKey, 0);
                        if (!edgeCounts.has(reverseKey)) edgeCounts.set(reverseKey, 0);

                        edgeCounts.set(edgeKey, edgeCounts.get(edgeKey) + 1);
                    }
                }
            }
        }

        let finalEdges = new Map();

        for (const [key, count] of edgeCounts.entries()) {
            const [_, target, source] = key.split("|"); 
            const reverseKey = `edge|${source}|${target}`;

            if (finalEdges.has(reverseKey)) continue;

            if (edgeCounts.has(reverseKey)) {

                const reverseCount = edgeCounts.get(reverseKey);
                if (count >= reverseCount) {
                    finalEdges.set(key, { target, source, count });
                } else {
                    finalEdges.set(reverseKey, { target: source, source: target, count: reverseCount });
                }
            } else {
                finalEdges.set(key, { target, source, count });
            }
        }

        const moduleEdges = Object.fromEntries(
            Array.from(finalEdges.entries()).map(([key, value]) => [key, { target: value.target, source: value.source }])
        );

        for (let [id, module] of Object.entries(moduleNodes)) {
            const moduleConcepts = module.concepts.map(item => item.name)
            const gNodes = new dagre.graphlib.Graph()

            gNodes.setGraph({
                align: this.layoutConfig.value.alignment,
                rankdir: this.layoutConfig.value.direction,
                nodesep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.nodeSeparation,
                edgesep: 0,
                ranksep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.rankSeparation,
                ranker: this.layoutConfig.value.ranker,
                acyclicer: this.layoutConfig.value.acyclicer
            })

            gNodes.setDefaultEdgeLabel(() => ({}))
        
            moduleConcepts.forEach((node) => {
                gNodes.setNode(node, { label: node, width: this.layoutConfig.value.nodeSize, height: this.layoutConfig.value.nodeSize })
            })
        
            Object.values(this.edges.value).forEach(edge => {
                if (moduleConcepts.includes(edge.source) && moduleConcepts.includes(edge.target) && !edge?.status || 'none' === 'delete') {
                    gNodes.setEdge(edge.source, edge.target)
                }
            })
            dagre.layout(gNodes)
            
            let tempLayouts = {nodes: {}}
            gNodes.nodes().forEach((nodeId) => {
                if (gNodes.node(nodeId)) {
                    const x = gNodes.node(nodeId).x
                    const y = gNodes.node(nodeId).y
                    tempLayouts.nodes[nodeId] = { x, y }
                }
            })
            moduleNodes[id].layouts = tempLayouts
            moduleNodes[id].width = gNodes._label.width
            moduleNodes[id].height = gNodes._label.height

        }

        const gTemp = new dagre.graphlib.Graph()

        gTemp.setGraph({
            align: this.layoutConfig.value.alignment,
            rankdir: this.layoutConfig.value.direction,
            nodesep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.nodeSeparation,
            edgesep: 0,
            ranksep: this.layoutConfig.value.nodeSize * this.layoutConfig.value.rankSeparation,
            ranker: this.layoutConfig.value.ranker,
            acyclicer: this.layoutConfig.value.acyclicer
        })

        gTemp.setDefaultEdgeLabel(() => ({}))

        Object.entries(moduleNodes).forEach(([nodeId, node]) => {
            gTemp.setNode(nodeId, { label: node.name, width: node.width * this.layoutConfig.value.groupScalingX, height: node.height * this.layoutConfig.value.groupScalingY })
        })
    
        Object.values(moduleEdges).forEach(edge => {
            gTemp.setEdge(edge.source, edge.target)
        })
        dagre.layout(gTemp)
        
        let testLayouts = {nodes: {}}
        gTemp.nodes().forEach((nodeId) => {
            if (gTemp.node(nodeId)) {
                const x = gTemp.node(nodeId).x
                const y = gTemp.node(nodeId).y
                testLayouts.nodes[nodeId] = { x, y }
            }
        })

        let nodeLayouts = {nodes: {}}
        for (let [id, module] of Object.entries(moduleNodes)) {
            const newOrigin = testLayouts.nodes[id]
            Object.entries(module.layouts.nodes).forEach(([nodeId, layout]) => {
                const xTranslated = layout.x + newOrigin.x
                const yTranslated = layout.y + newOrigin.y
                nodeLayouts.nodes[nodeId] = {x: xTranslated, y: yTranslated}
            })
        }

        // this.nodes.value = moduleNodes
        // this.edges.value = moduleEdges
        // this.layouts.nodes = testLayouts.nodes
        this.layouts.nodes = nodeLayouts.nodes
    }

    saveChangeRequests = () => {
        for (let [entityId, reqData] of Object.entries(this.changeRequestDrafts.value)) {
            let status = 'pending'
            if (reqData.type === "node") {
                status = 'approved'
            }
            axios.put(`${this.tool_domain}/domain/changes/status?change_request_id=${reqData.reqId}&status=${status}`).then(() => {
                delete this.changeRequestDrafts.value[entityId]
            })
        }
    }
    deleteChangeRequest = (entityId) => {
        axios.delete(`${this.tool_domain}/domain/changes/draft?change_request_id=${this.changeRequestDrafts.value[entityId].reqId}`).then(() => {
            delete this.changeRequestDrafts.value[entityId]
        })
    }

    addNewCollection = (collectionObj) => {
        axios.post(`${this.tool_domain}/course/collection`, collectionObj).then((response) => {
            collectionObj.id = response.data.id
            this.collections.value.push(collectionObj)
        })
    }

    RemoveSelectedNodesFromModule = () => {
        const newModule = this.selectedModule.value
        let junctionObjs = []

        for (let nodeId of this.selectedNodes.value) {
            const node = this.nodes.value[nodeId]

            if (node.is_saved) {
                junctionObjs.push(
                    {
                        "concept_name": node.name,
                        "collection_id": newModule
                    }
                ) 
            } else {
                // Simplest solution for handling newly created nodes is to prevent their inclusion in the action until they have been saved.
                // TODO: Add custom svg for displaying the alert
                this.nodes.value[nodeId]['alert'] = "Node must be saved prior to additional changes" 
            }
        }

        if (junctionObjs.length > 0) {
            axios.delete(`${this.tool_domain}/course/collection`, {data: junctionObjs}).then(() => {
                for (let junction of junctionObjs) {
                    const updatedModules = this.nodes.value[junction.concept_name].module.filter(oldModule => oldModule !== junction.collection_id)
                    if (updatedModules.length > 0) {
                        this.nodes.value[junction.concept_name].module = updatedModules
                    } else {
                        delete this.nodes.value[junction.concept_name]
                    }
                }
            })
        }
    }

    addSelectedNodesToModule = () => {
        const newModule = this.selectedModule.value
        let junctionObjs = []

        for (let nodeId of this.selectedNodes.value) {
            const node = this.nodes.value[nodeId]
            if (node.is_saved) {
                junctionObjs.push(
                    {
                        "concept_name": node.name,
                        "collection_id": newModule
                    }
                ) 
            } else {
                // Simplest solution for handling newly created nodes is to prevent their inclusion in the action until they have been saved.
                // TODO: Add custom svg for displaying the alert
                this.nodes.value[nodeId]['alert'] = "Node must be saved prior to additional changes" 
            }
        }

        axios.post(`${this.tool_domain}/course/collection/concept`, junctionObjs).then(() => {
            for (let junction of junctionObjs) {
                this.nodes.value[junction.concept_name].module.push(newModule)
            }
        })

    }


    /**
     * Creates a change request as a draft for adding a new node, promoted to approved upon saving.
     * @category Domain Editor - Nodes
     */
    addNode = (node) => {
        let changeRequest = {
            is_from_llm: false,
            post_approval_procedure: {
                type: "junction", 
                target_id: this.selectedModule.value,
                target_table: "module"
            },
            entity_data: {
                name: node.name,
                subject: node.subject,
                summary: node?.summary || '',
                difficulty: node?.difficulty || 1
            },
            entity_type: "concept",
            modification_type: "create",
            validation_status: "draft",
        }

        axios.post(`${this.tool_domain}/domain/changes`, changeRequest).then((response) => {
            this.changeRequestDrafts.value[node.id] = {reqId: response.data.id, type: 'node'}
            this.nodes.value[node.id] = {...node, is_saved: false, module: [this.selectedModule.value], params: {}}
            this.replaceParams([{node: node.id, params: {"focusColor": "#4cff30"}}])
            this.focusNode.value = node.id
        })

        
    }

    addExistingNode = (node) => {
        const junctionObj = [
            {
                "concept_name": node.name,
                "collection_id": this.selectedModule.value
            }
        ]
        axios.post(`${this.tool_domain}/course/collection/concept`, junctionObj).then(() => {
            this.nodes.value[node.id] = {...node, is_saved: true, module: [this.selectedModule.value], params: {}}
            this.replaceParams([{node: node.id, params: {"focusColor": "#4cff30"}}])
            this.focusNode.value = node.id
        })
    }

    /**
     * Removes a node at the course-domain level, course-domains are defined by the contents of all associated collections,
     * so by removing a node from all collections we effectively remove the node from the course. 
     * This method does not delete the node entirely from the DB, in turn no Change Request is required for this action.
     */
    deleteSelectedNodes = () => {
        for (let nodeId of this.selectedNodes.value) {
            // We delete the edges first, this is done so in future when change history is tracked we can reverse our steps in a logical order.
            // This will require the node deletion to be last, that way its the first action undone when retracing our steps before we add the edges back.
            // If we didn't, then we risk trying to add edges back that have no node to connect to, resulting in an error.

            this.deleteAllNodeEdges(nodeId)
            const node = this.nodes.value[nodeId]
            let junctionObjs = []
            for (let moduleId of node.module) {
                junctionObjs.push(
                    {
                        "concept_name": node.name,
                        "collection_id": moduleId
                    }
                )
            }
            if (this.changeRequestDrafts.value[nodeId]) {
                this.deleteChangeRequest(nodeId)
                delete this.nodes.value[nodeId]

            } else {
                axios.delete(`${this.tool_domain}/course/collection`, {data: junctionObjs}).then(() => {
                    delete this.nodes.value[nodeId]
                })

            }
        }
    }


    /**
     * Creates a change request for new edges between concepts
     * @category Domain Editor - Edges
     */
    addSelectedEdges = () => {
        const edgeValues = Object.values(this.edges.value)
        for (let node of this.selectedNodes.value) {
            // checks if the new edge already exists and that the new edge doesn't contain nodes linked to themselves
            const newEdge = {source: node, target: this.focusNode.value, is_saved: false, status: "create"}

            if (!edgeValues.some(node => JSON.stringify(node) === JSON.stringify(newEdge)) && newEdge.source !== newEdge.target) {
                
                let changeRequest = {
                    is_from_llm: false,
                    post_approval_procedure: {},
                    entity_data: {concept_name: newEdge.target, prereq_name: newEdge.source},
                    entity_type: "concept_to_concept",
                    modification_type: "create",
                    validation_status: "draft",
                }

                const edgeKey = `edge|${newEdge.source}|${newEdge.target}`

                axios.post(`${this.tool_domain}/domain/changes`, changeRequest).then((response) => {
                    this.changeRequestDrafts.value[edgeKey] = {reqId: response.data.id, type: 'edge'}
                    this.edges.value[edgeKey] = newEdge

                })
            }

        }
    }

    /**
     * Creates a change request to remove edges between concepts
     * @category Domain Editor - Edges
     */
    deleteSelectedEdges = () => {
        for (let edgeId of this.selectedEdges.value) {
            const entity_data = {concept_name: this.edges.value[edgeId].target, prereq_name: this.edges.value[edgeId].source}
            let changeRequest = {
                is_from_llm: false,
                post_approval_procedure: {},
                entity_id: edgeId,
                entity_data: entity_data,
                entity_type: "concept_to_concept",
                modification_type: "delete",
                validation_status: "draft",
            }

            if (this.changeRequestDrafts.value[edgeId]) {
                this.deleteChangeRequest(edgeId)
                delete this.edges.value[edgeId]

            } else {
                axios.post(`${this.tool_domain}/domain/changes`, changeRequest).then((response) => {
                    this.changeRequestDrafts.value[edgeId] = {reqId: response.data.id, type: 'edge'}
                    this.edges.value[edgeId].is_saved = false
                    this.edges.value[edgeId].status = "delete"
    
                })
            }
        }
        this.selectedEdges.value = []
    }

    /**
     * WARNING: This method only operates locally and does not delete any edges from the DB.
     * This is a cleanup method that deletes all edges connected to a node from Frontend state only, intended for use when a node is being removed from the course-domain.
     * This action is optional and does not require edges being deleted from the wider domain.
     * @category Utility - Edges
     * @param {String} nodeId The Key of the node we are deleting all edges from, edges use a structured string containing node IDs, so any edge key containing the node ID in its key is deleted locally.
     */
    deleteAllNodeEdges = (nodeId) => {
        // creates a list of edge ids containing the id of the node being deleted
        // edge id must be formatted as 'edge-{source node id}-{target node id}' for the split and filter statement to work properly
        const validEdgeIds = Object.keys(this.edges.value).filter(key => key.split("|").includes(nodeId))
        for (let edgeId of validEdgeIds) {
            delete this.edges.value[edgeId]
        }
    }


    /**
     * Updates the lookup table for selected nodes and focus node as well as param clearing
     * @category Reference Update
     * @param {*} _ 
     * @param {*} event 
     */
    onNodeSelect = (_, event) => {
        if (event.length === 1) {
            this.replaceParams([{node: event[0], params: {"focusColor": this.styles.focusColor}}])
            this.replaceParams([{node: this.focusNode.value, params: {}}])
            this.focusNode.value = event[0]
        }

        if (event.length === 0) {
            this.replaceParams([{node: this.focusNode.value, params: {}}])
        }

        this.selectedNodes.value = event
        
    }

    onEdgeSelect = (_, event) => {
        this.selectedEdges.value = event
    }

    onNodeHover = (type, event) => {
        if (type === "node:pointerout") {
            this.nodeHovered.value = null
        } else (
            this.nodeHovered.value = event.node
        )
    }

    onModeUpdate = (_, event) => {
        this.isBoxSelectionMode.value = event === "box-selection"
    }

    updateSelectedNodes = (mode, value=null) => {
        switch (mode) {
        case "push":
            this.selectedNodes.value.push(value)
            break;

        case "update":
            this.selectedNodes.value = value
            break;
        default:
            this.selectedNodes.value = []
            break;
        }
    }

    updateSelectedModule = (moduleId) => {
        this.selectedModule.value = moduleId
    }



    /**
     * Replaces the values of specific keys contained within the 'params' object attached to a node. 
     * Allows specific sub-params to update and maintains the lookup table for nodes with active params
     * @param {Array[Object]} paramSpecs Array of objects specifying the node to target and the keys and values to modify on the params object. Structure Ex. [{node: <id of node>, params: {'param key': <new value>}}] 
     */
    replaceParams = (paramSpecs=[]) => {
        for (let item of paramSpecs) {
            this.nodes.value[item.node] ? this.nodes.value[item.node].params = item.params : null

            if (Object.keys(item.params).length === 0) {
                this.paramNodes.delete(item.node)
            } 
            else {
                this.paramNodes.add(item.node)
            }
        }
    }

    clearParams = () => {
        this.paramNodes.forEach(item => this.nodes.value[item].params = {})
        this.paramNodes.clear()
        this.selectedEdges.value = []
        this.selectedNodes.value = []
        this.focusNode.value = null
    }



    saveDomain = async () => {
        await axios.put(`${window.contextData.tool_domain}/domain`, this.changeHistory)
    }

    saveDomainToJSON = () => {
        this.saving.value = true

        const date = new Date().toDateString()
        const fileName = `domain_model_${date}.json`
        const currentDomain = {"nodes": this.nodes.value, "edges": this.edges.value, "collections": this.collections.value}

        const blob = new Blob([JSON.stringify(currentDomain)], {type: "text/plain"})
        const downloadURL = window.URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = downloadURL;
        link.target = '_blank';
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.saving.value = false
    }

    

    /**
     * Used during Transitive Reduction operations
     * @category Internal Utility Method
     *
     */
    _buildAdjacencyList = (edges) => {
        const adjacencyList = {};
        for (const key in edges) {
            const { source, target } = edges[key];
            if (!adjacencyList[source]) {
            adjacencyList[source] = [];
            }
            adjacencyList[source].push(target);
        }
        return adjacencyList;
    }

    /**
     * Used during Transitive Reduction operations
     * @category Internal Utility Method
     *
     */
    _dfs = (node, adjacencyList, visited) => {
        if (visited.has(node)) {
            return visited.get(node);
        }
    
        const reachable = new Set();
        if (adjacencyList[node]) {
            for (const neighbor of adjacencyList[node]) {
            reachable.add(neighbor);
            const reachableFromNeighbor = this._dfs(neighbor, adjacencyList, visited);
            for (const item of reachableFromNeighbor) {
                reachable.add(item);
            }
            }
        }
    
        visited.set(node, reachable);
        return reachable;
    }

    /**
     * Used during Transitive Reduction operations
     * @category Internal Utility Method
     *
     */
    _findAllReachable = (adjacencyList) => {
        const reachableMap = new Map();
        for (const node in adjacencyList) {
            this._dfs(node, adjacencyList, reachableMap);
        }
        return reachableMap;
    }
    
    transitiveReduction = () => {
        const edges = this.edges.value
        const adjacencyList = this._buildAdjacencyList(edges);
        const reachableMap = this._findAllReachable(adjacencyList);
        // const reducedEdges = {};
        const removedEdges = []
    
        for (const key in edges) {
            const { source, target } = edges[key];
            const reachableFromSource = new Set(reachableMap.get(source));
            reachableFromSource.delete(target); // Remove the direct edge to avoid self-loop check
    
            // Check if the target is reachable from the source through another path
            let isIndirectlyReachable = false;
            for (const intermediate of reachableFromSource) {
            if (reachableMap.get(intermediate) && reachableMap.get(intermediate).has(target)) {
                isIndirectlyReachable = true;
                break;
            }
            }
    
            if (isIndirectlyReachable) {
                removedEdges.push(key)
            }
        }
    
        this.selectedEdges.value = removedEdges
    }
}

