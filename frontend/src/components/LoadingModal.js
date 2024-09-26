import React from 'react';
import { Modal, Spinner } from 'react-bootstrap';

const LoadingModal = ({ isOpen, onRequestClose, message = "Chargement en cours..." }) => {
    return (
        <Modal show={isOpen} onHide={onRequestClose} centered backdrop="static" keyboard={false}>
            <Modal.Body className="text-center">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Chargement...</span>
                </Spinner>
                <p>{message}</p>
            </Modal.Body>
        </Modal>
    );
};

export default LoadingModal;