import React from 'react';
import './Modal.css';

function ConfirmModal({ isOpen, message, onConfirm, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="modal open">
      <div className="modal-content">
        <p>{message}</p>
        <span className="yes"><button className="yes" onClick={onConfirm}>Yes</button></span>
        <span className="no"><button className="no" onClick={onCancel}>No</button></span>
      </div>
    </div>
  );
}

export default ConfirmModal;
