import React, { useState } from 'react';
import { Modal, Tab, Tabs, Button } from 'react-bootstrap';
import MO_gemapiTab from './MO_gemapiTab';
import './TabImportShpModal.css';

const TabImportShpModal = ({ isOpen, onRequestClose, initialBounds }) => {
    const [activeTab, setActiveTab] = useState('MO_gemapi');

    if (!isOpen) return null; // Ne rien rendre si le modal n'est pas ouvert

    return (
        <Modal show={isOpen} onHide={onRequestClose} centered className="modal-lg">
            <Modal.Header closeButton>
                <Modal.Title>Importer des polygones manquants</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {isOpen && (
                    <Tabs
                        id="controlled-tab-example"
                        activeKey={activeTab}
                        onSelect={(k) => setActiveTab(k)}
                        className="mb-3"
                    >
                    <Tab eventKey="MO_gemapi" title="MO_gemapi">
                        <MO_gemapiTab initialBounds={initialBounds} />
                    </Tab>
                        <Tab eventKey="tab2" title="Onglet 2">
                            <div>Contenu pour Onglet 2</div>
                        </Tab>
                        <Tab eventKey="tab3" title="Onglet 3">
                            <div>Contenu pour Onglet 3</div>
                        </Tab>
                    </Tabs>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onRequestClose}>
                    Fermer
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default TabImportShpModal;
