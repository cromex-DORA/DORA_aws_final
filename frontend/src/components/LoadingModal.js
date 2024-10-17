import React from 'react';
import { Modal, Spinner } from 'react-bootstrap';
import './LoadingModal.css';

const LoadingModal = ({ isOpen, onRequestClose, message = "Chargement en cours..." }) => {
    return (
        <Modal 
            show={isOpen} 
            onHide={onRequestClose} 
            centered 
            backdrop="static" 
            keyboard={false}
            className="loading-modal" // Appliquez une classe CSS personnalisée à la modal
        >
            <Modal.Body className="loading-modal-body text-center">
                <Spinner animation="border" role="status" className="loading-spinner">
                    <span className="visually-hidden">Chargement...</span>
                </Spinner>
                <p className="loading-message">{message}</p>
            </Modal.Body>
        </Modal>
    );
};

export default LoadingModal;
