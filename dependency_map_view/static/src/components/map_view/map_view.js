/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";

export class DependencyMapRenderer extends Component {
    static template = "dependency_map_view.MapView";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.containerRef = useRef("mapContainer");
        this.state = useState({ 
            loading: false,
            records: [],
            selectedRecord: null,
        });
        this.network = null;

        onMounted(() => this.loadRecords());
        onWillUnmount(() => {
            if (this.network) this.network.destroy();
        });
    }

    async loadRecords() {
        this.state.loading = true;
        const model = this.props.resModel || 'res.partner';
        const records = await this.orm.searchRead(model, [], ['id', 'display_name'], { limit: 50 });
        this.state.records = records;
        this.state.loading = false;
    }

    async selectRecord(record) {
        this.state.selectedRecord = record;
        await this.renderMap(record);
    }

    async renderMap(record) {
        if (!record) return;
        
        this.state.loading = true;
        const model = this.props.resModel || 'res.partner';
        
        const nodes = [];
        const edges = [];
        
        nodes.push({
            id: record.id,
            label: record.display_name,
            shape: 'box',
            color: { background: '#9b59b6', border: '#8e44ad' },
            font: { size: 14, color: '#ffffff', bold: true },
            margin: 10,
            level: 0,
        });
        
        const fields = await this.orm.call(model, 'fields_get', [], {
            attributes: ['type', 'relation', 'string']
        });
        
        for (const [fieldName, fieldInfo] of Object.entries(fields)) {
            if (!['many2one', 'one2many', 'many2many'].includes(fieldInfo.type)) continue;
            if (!fieldInfo.relation) continue;
            if (fieldInfo.relation.includes('mail.') || fieldInfo.relation.includes('ir.')) continue;
            
            const fullRecord = await this.orm.searchRead(model, [['id', '=', record.id]], [fieldName]);
            
            if (fullRecord.length > 0 && fullRecord[0][fieldName]) {
                const relValue = fullRecord[0][fieldName];
                const isManyToOne = fieldInfo.type === 'many2one';
                
                // Handle many2one fields (single relationship)
                if (isManyToOne) {
                    let relId, relName;
                    
                    // Case 1: [id, name] tuple format
                    if (Array.isArray(relValue) && relValue.length === 2 && typeof relValue[0] === 'number') {
                        relId = relValue[0];
                        relName = relValue[1];
                    }
                    // Case 2: Just ID (number)
                    else if (typeof relValue === 'number') {
                        relId = relValue;
                        try {
                            const relRecords = await this.orm.searchRead(fieldInfo.relation, [['id', '=', relId]], ['display_name']);
                            relName = relRecords[0]?.display_name || `ID: ${relId}`;
                        } catch (e) {
                            relName = `ID: ${relId}`;
                        }
                    }
                    
                    if (relId) {
                        const relNodeId = `${fieldInfo.relation}_${relId}_${fieldName}`;
                        if (!nodes.find(n => n.id === relNodeId)) {
                            nodes.push({
                                id: relNodeId,
                                label: relName,
                                shape: 'box',
                                color: { background: '#f39c12', border: '#e67e22' },
                                font: { size: 12, color: '#ffffff' },
                                margin: 8,
                                level: -1,
                            });
                        }
                        edges.push({
                            from: relNodeId,
                            to: record.id,
                            arrows: 'to',
                            label: fieldInfo.string,
                            color: { color: '#e67e22' },
                            width: 2,
                        });
                    }
                }
                // Handle one2many and many2many fields (multiple relationships)
                else if (Array.isArray(relValue) && relValue.length > 0) {
                    const isManyToMany = fieldInfo.type === 'many2many';
                    const nodeColor = isManyToMany 
                        ? { background: '#27ae60', border: '#229954' }  // Green for many2many
                        : { background: '#3498db', border: '#2980b9' };  // Blue for one2many
                    const edgeStyle = isManyToMany ? { dashes: [5, 5] } : {};
                    
                    const validIds = relValue.filter(id => typeof id === 'number');
                    for (const relId of validIds) {
                        try {
                            const relRecords = await this.orm.searchRead(fieldInfo.relation, [['id', '=', relId]], ['id', 'display_name']);
                            if (relRecords.length > 0) {
                                const relNodeId = `${fieldInfo.relation}_${relId}`;
                                if (!nodes.find(n => n.id === relNodeId)) {
                                    nodes.push({
                                        id: relNodeId,
                                        label: relRecords[0].display_name || `ID: ${relId}`,
                                        shape: 'box',
                                        color: nodeColor,
                                        font: { size: 12, color: '#ffffff' },
                                        margin: 8,
                                        level: 1,
                                    });
                                }
                                const edgeColor = isManyToMany ? '#229954' : '#2980b9';
                                edges.push({
                                    from: record.id,
                                    to: relNodeId,
                                    arrows: 'to',
                                    label: fieldInfo.string,
                                    color: { color: edgeColor },
                                    width: 2,
                                });
                            }
                        } catch (e) {
                            console.error('Error fetching relation:', fieldName, relId, e);
                        }
                    }
                }
            }
        }
        
        this.drawNetwork(nodes, edges);
        this.state.loading = false;
    }

    drawNetwork(nodes, edges) {
        if (this.network) this.network.destroy();
        
        const container = this.containerRef.el;
        const data = { nodes, edges };
        const options = {
            layout: { 
                hierarchical: { 
                    enabled: true, 
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 200,
                    treeSpacing: 250,
                    blockShifting: true,
                    edgeMinimization: true,
                    parentCentralization: true,
                } 
            },
            physics: { enabled: false },
            nodes: { 
                shape: 'box',
                font: { 
                    size: 13, 
                    face: 'Arial',
                    color: '#ffffff'
                },
                borderWidth: 2,
                borderWidthSelected: 3,
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.2)',
                    size: 10,
                    x: 3,
                    y: 3
                },
                margin: 10,
                widthConstraint: {
                    minimum: 120,
                    maximum: 250
                }
            },
            edges: {
                width: 2,
                font: { 
                    size: 11,
                    color: '#666666',
                    background: '#ffffff',
                    strokeWidth: 0
                },
                smooth: { 
                    enabled: true,
                    type: 'cubicBezier',
                    roundness: 0.5
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.8
                    }
                }
            },
            interaction: {
                hover: true,
                zoomView: true,
                dragView: true,
                selectConnectedEdges: false
            }
        };
        
        this.network = new vis.Network(container, data, options);
        
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                let model, id;
                
                if (typeof nodeId === 'number') {
                    model = this.props.resModel;
                    id = nodeId;
                } else {
                    [model, id] = nodeId.split('_');
                    id = parseInt(id);
                }
                
                this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: model,
                    res_id: id,
                    views: [[false, 'form']],
                    target: 'new',
                });
            }
        });
    }
}

export class DependencyMapController extends Component {
    static template = "dependency_map_view.MapController";
    static components = { Layout, DependencyMapRenderer };
    static props = ["*"];
}

export const dependencyMapView = {
    type: "dependency_map",
    display_name: "Dependency Map",
    icon: "fa fa-code-fork",
    multiRecord: true,
    Controller: DependencyMapController,
};

registry.category("views").add("dependency_map", dependencyMapView);
