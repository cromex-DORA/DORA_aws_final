import React from 'react';
import { Modal } from 'react-bootstrap';
import './SuccessModal.css';

const SuccessModal = ({ isOpen, onRequestClose, message }) => {
    return (
        <Modal
            show={isOpen}
            onHide={onRequestClose}
            centered
            className="custom-success-modal" // Appliquer la classe personnalisée
        >
            <Modal.Header closeButton>
                <Modal.Title>Succès !</Modal.Title>
            </Modal.Header>
            <Modal.Body className="text-center">
                {message}
                <button className="btn btn-primary" onClick={onRequestClose}>Fermer</button>
            </Modal.Body>
        </Modal>
    );
};

export default SuccessModal;
