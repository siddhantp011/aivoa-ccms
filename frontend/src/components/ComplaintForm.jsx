import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fieldChanged, resetForm, saveComplaint } from '../store/complaintSlice'

const SEVERITY_OPTIONS = ['Minor', 'Major', 'Critical']
const PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Urgent']

function Field({ label, name, value, onChange, type = 'text', placeholder = 'Awaiting AI extraction...' }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        className="field-input"
        type={type}
        name={name}
        value={value || ''}
        placeholder={placeholder}
        onChange={(e) => onChange(name, e.target.value)}
      />
    </label>
  )
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <select className="field-input" name={name} value={value || ''} onChange={(e) => onChange(name, e.target.value)}>
        <option value="">Awaiting AI extraction...</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </label>
  )
}

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const { id, fields, ai, status } = useSelector((s) => s.complaint)

  const onChange = (name, value) => dispatch(fieldChanged({ name, value }))

  const onSave = () => {
    if (!id) return
    dispatch(saveComplaint({ id, fields }))
  }

  return (
    <section className="panel complaint-form">
      <div className="panel-header-row">
        <span className="status-badge">{status === 'ready' || status === 'saving' ? (fields.detailed_complaint_description ? 'Pending Triage' : 'Pending Triage') : 'Pending Triage'}</span>
      </div>

      {ai.completeness_score !== null && ai.completeness_score !== undefined && (
        <div className="ai-insight-bar">
          <div className="insight-item">
            <span className="insight-label">Completeness</span>
            <div className="progress-track"><div className="progress-fill" style={{ width: `${ai.completeness_score}%` }} /></div>
            <span className="insight-value">{ai.completeness_score}%</span>
          </div>
          {ai.risk_classification && (
            <div className={`risk-pill risk-${ai.risk_classification.toLowerCase()}`}>
              AI Risk: {ai.risk_classification}
            </div>
          )}
          {ai.missing_fields?.length > 0 && (
            <div className="missing-fields">Missing: {ai.missing_fields.join(', ')}</div>
          )}
        </div>
      )}

      <fieldset className="form-section">
        <legend>1. Origin &amp; Customer Details</legend>
        <div className="field-grid">
          <Field label="Complaint Source" name="complaint_source" value={fields.complaint_source} onChange={onChange} />
          <Field label="Customer Name" name="customer_name" value={fields.customer_name} onChange={onChange} />
        </div>
      </fieldset>

      <fieldset className="form-section">
        <legend>2. Product &amp; Batch Identification</legend>
        <div className="field-grid">
          <Field label="Product Name" name="product_name" value={fields.product_name} onChange={onChange} />
          <Field label="Product Strength/Grade" name="product_strength_grade" value={fields.product_strength_grade} onChange={onChange} />
          <Field label="Batch/Lot Number" name="batch_lot_number" value={fields.batch_lot_number} onChange={onChange} />
          <Field label="Manufacturing Date" name="manufacturing_date" type="date" value={fields.manufacturing_date} onChange={onChange} />
          <Field label="Expiry Date" name="expiry_date" type="date" value={fields.expiry_date} onChange={onChange} />
          <Field label="Quantity Affected" name="quantity_affected" value={fields.quantity_affected} onChange={onChange} />
        </div>
      </fieldset>

      <fieldset className="form-section">
        <legend>3. Complaint Details</legend>
        <div className="field-grid">
          <Field label="Complaint Type" name="complaint_type" value={fields.complaint_type} onChange={onChange} />
          <Field label="Complaint Date" name="complaint_date" type="date" value={fields.complaint_date} onChange={onChange} />
        </div>
        <label className="field field-full">
          <span className="field-label">Detailed Complaint Description</span>
          <textarea
            className="field-input textarea"
            name="detailed_complaint_description"
            value={fields.detailed_complaint_description || ''}
            placeholder="Awaiting AI extraction..."
            onChange={(e) => onChange('detailed_complaint_description', e.target.value)}
          />
        </label>
      </fieldset>

      <fieldset className="form-section">
        <legend>4. Initial Assessment &amp; Priority</legend>
        <div className="field-grid">
          <SelectField label="Initial Severity" name="initial_severity" value={fields.initial_severity} onChange={onChange} options={SEVERITY_OPTIONS} />
          <SelectField label="Priority" name="priority" value={fields.priority} onChange={onChange} options={PRIORITY_OPTIONS} />
        </div>
      </fieldset>

      {ai.risk_rationale && (
        <p className="risk-rationale"><strong>AI rationale:</strong> {ai.risk_rationale}</p>
      )}

      <div className="form-actions">
        <button className="btn btn-secondary" onClick={() => dispatch(resetForm())}>Reset Form</button>
        <button className="btn btn-primary" disabled={!id || status === 'saving'} onClick={onSave}>
          {status === 'saving' ? 'Saving...' : 'Save Complaint'}
        </button>
      </div>
    </section>
  )
}
