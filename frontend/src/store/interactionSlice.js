import { createSlice } from '@reduxjs/toolkit'

const initialFormData = {
  id: null,
  hcp_name: '',
  interaction_type: 'Meeting',
  date: '',
  time: '',
  attendees: '',
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
  ai_suggested_followups: [],
}

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: {
    formData: initialFormData,
    savedInteractions: [],
    isSaving: false,
    lastSaved: null,
  },
  reducers: {
    updateFormData(state, action) {
      state.formData = { ...state.formData, ...action.payload }
    },
    resetForm(state) {
      state.formData = initialFormData
    },
    setFormFromAI(state, action) {
      // Replace form data from AI tool result
      state.formData = { ...state.formData, ...action.payload }
    },
    addSavedInteraction(state, action) {
      const idx = state.savedInteractions.findIndex(i => i.id === action.payload.id)
      if (idx >= 0) {
        state.savedInteractions[idx] = action.payload
      } else {
        state.savedInteractions.unshift(action.payload)
      }
      state.lastSaved = new Date().toISOString()
    },
    setSaving(state, action) {
      state.isSaving = action.payload
    },
  },
})

export const { updateFormData, resetForm, setFormFromAI, addSavedInteraction, setSaving } =
  interactionSlice.actions
export default interactionSlice.reducer