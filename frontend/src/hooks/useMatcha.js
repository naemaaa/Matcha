import { useState, useCallback } from 'react'

import { sendMessage, uploadFile, analyzeJob, reviewDocument } from '../utils/api'

import { v4 as uuidv4 } from 'uuid'

export const useMatcha = () => {

  const [sessionId] = useState(() => uuidv4().slice(0, 8))

  const [chatHistory, setChatHistory] = useState([])

  const [agentState, setAgentState] = useState({

    messages: [],

    profile_complete: false,

    drift_detected: false,

    previous_intent_history: [],

  })

  const [isLoading, setIsLoading] = useState(false)

  const sendChat = useCallback(async (userInput) => {

    setIsLoading(true)

    setChatHistory(prev => [...prev, { role: 'user', content: userInput }])

    try {

      const result = await sendMessage(sessionId, userInput, agentState)

      setAgentState(result.agent_state)

      setChatHistory(prev => [...prev, { role: 'assistant', content: result.response }])

      return result

    } catch (error) {

      console.error('Error:', error)

      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Maaf, terjadi error. Coba lagi.' }])

    } finally {

      setIsLoading(false)

    }

  }, [sessionId, agentState])

  const uploadDocument = useCallback(async (file, fileType) => {

    setIsLoading(true)

    try {

      const result = await uploadFile(sessionId, file, fileType)

      setAgentState(prev => ({

        ...prev,

        [fileType === 'cv' ? 'cv_text' : 'linkedin_text']: result.extracted_text,
        [fileType === 'cv' ? 'cv_uploaded' : 'linkedin_uploaded']: true

      }))

      return result

    } catch (error) {

      console.error('Error:', error)

    } finally {

      setIsLoading(false)

    }

  }, [sessionId])

  const reviewDocumentFull = useCallback(async (documentType) => {

    setIsLoading(true)

    try {

      const result = await reviewDocument(sessionId, documentType, agentState)

      // Merge extracted data into agentState
      setAgentState(prev => ({

        ...prev,

        ...result.agent_state,

        [documentType === 'cv' ? 'cv_reviewed' : 'linkedin_reviewed']: true,

        user_profile: {
          ...prev.user_profile,
          ...result.extracted_data,
        },

        // Merge extracted skills into existing skills
        extracted_skills: [
          ...(prev.extracted_skills || []),
          ...(result.extracted_data?.skills || [])
        ]

      }))

      setChatHistory(prev => [...prev, { role: 'assistant', content: result.response }])

      return result

    } catch (error) {

      console.error('Error reviewing document:', error)

    } finally {

      setIsLoading(false)

    }

  }, [sessionId, agentState])

  const analyzeJobDescription = useCallback(async (jobDescription) => {

    setIsLoading(true)

    try {

      const result = await analyzeJob(sessionId, jobDescription, agentState)

      setAgentState(result.agent_state)

      setChatHistory(prev => [...prev, { role: 'assistant', content: result.response }])

      return result


    } catch (error) {

      console.error('Error:', error)

    } finally {

      setIsLoading(false)

    }

  }, [sessionId, agentState])

  return {

    sessionId,

    chatHistory,

    agentState,

    isLoading,

    sendChat,

    uploadDocument,

    reviewDocumentFull,

    analyzeJobDescription,

  }

}