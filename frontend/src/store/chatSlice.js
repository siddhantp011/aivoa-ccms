import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '../api/client'

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ complaintId, message }) => {
    const { data } = await api.post('/api/chat', { complaint_id: complaintId, message })
    return { userMessage: message, reply: data.reply }
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      { role: 'assistant', text: 'Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.' },
    ],
    sending: false,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.sending = true
        state.messages.push({ role: 'user', text: action.meta.arg.message })
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.sending = false
        state.messages.push({ role: 'assistant', text: action.payload.reply })
      })
      .addCase(sendMessage.rejected, (state) => {
        state.sending = false
        state.messages.push({ role: 'assistant', text: 'Sorry, something went wrong reaching the assistant.' })
      })
  },
})

export default chatSlice.reducer
