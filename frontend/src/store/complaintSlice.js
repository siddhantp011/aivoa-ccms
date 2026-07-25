import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '../api/client'

const emptyComplaint = {
  complaint_source: '', customer_name: '',
  product_name: '', product_strength_grade: '',
  batch_lot_number: '', manufacturing_date: '', expiry_date: '', quantity_affected: '',
  complaint_type: '', complaint_date: '', detailed_complaint_description: '',
  initial_severity: '', priority: '',
}

export const extractFromText = createAsyncThunk(
  'complaint/extractFromText',
  async (rawText) => {
    const { data } = await api.post('/api/complaints/extract', { raw_text: rawText })
    return data
  }
)

export const extractFromFile = createAsyncThunk(
  'complaint/extractFromFile',
  async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/api/complaints/extract-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  }
)

export const saveComplaint = createAsyncThunk(
  'complaint/save',
  async ({ id, fields }) => {
    const { data } = await api.put(`/api/complaints/${id}`, fields)
    return data
  }
)

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    id: null,
    fields: emptyComplaint,
    ai: { completeness_score: null, missing_fields: [], risk_classification: null, risk_rationale: null },
    status: 'idle', // idle | extracting | ready | saving | error
    progressMessage: '',
    error: null,
  },
  reducers: {
    fieldChanged(state, action) {
      const { name, value } = action.payload
      state.fields[name] = value
    },
    resetForm(state) {
      state.id = null
      state.fields = { ...emptyComplaint }
      state.ai = { completeness_score: null, missing_fields: [], risk_classification: null, risk_rationale: null }
      state.status = 'idle'
    },
  },
  extraReducers: (builder) => {
    const handleExtractPending = (state) => {
      state.status = 'extracting'
      state.progressMessage = 'Analyzing document content and extracting key details...'
      state.error = null
    }
    const handleExtractFulfilled = (state, action) => {
      const data = action.payload
      state.id = data.id
      state.fields = {
        complaint_source: data.complaint_source || '',
        customer_name: data.customer_name || '',
        product_name: data.product_name || '',
        product_strength_grade: data.product_strength_grade || '',
        batch_lot_number: data.batch_lot_number || '',
        manufacturing_date: data.manufacturing_date || '',
        expiry_date: data.expiry_date || '',
        quantity_affected: data.quantity_affected || '',
        complaint_type: data.complaint_type || '',
        complaint_date: data.complaint_date || '',
        detailed_complaint_description: data.detailed_complaint_description || '',
        initial_severity: data.initial_severity || '',
        priority: data.priority || '',
      }
      state.ai = {
        completeness_score: data.completeness_score,
        missing_fields: data.missing_fields || [],
        risk_classification: data.risk_classification,
        risk_rationale: data.risk_rationale,
      }
      state.status = 'ready'
    }
    const handleExtractRejected = (state, action) => {
      state.status = 'error'
      state.error = action.error.message
    }

    builder
      .addCase(extractFromText.pending, handleExtractPending)
      .addCase(extractFromText.fulfilled, handleExtractFulfilled)
      .addCase(extractFromText.rejected, handleExtractRejected)
      .addCase(extractFromFile.pending, handleExtractPending)
      .addCase(extractFromFile.fulfilled, handleExtractFulfilled)
      .addCase(extractFromFile.rejected, handleExtractRejected)
      .addCase(saveComplaint.pending, (state) => { state.status = 'saving' })
      .addCase(saveComplaint.fulfilled, (state) => { state.status = 'ready' })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.status = 'error'
        state.error = action.error.message
      })
  },
})

export const { fieldChanged, resetForm } = complaintSlice.actions
export default complaintSlice.reducer
