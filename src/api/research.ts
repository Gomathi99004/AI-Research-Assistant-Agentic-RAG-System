import axios from 'axios'
import { QueryRequest, ResearchResponse } from '../types/research'

const api = axios.create({
  baseURL: '/api'
})

export async function submitQuery(request: QueryRequest): Promise<ResearchResponse> {
  const response = await api.post('/ask', request)
  return response.data
}

export async function uploadPdf(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function fetchDocuments(): Promise<{documents: {title: string}[]}> {
  const response = await api.get('/documents')
  return response.data
}

export async function deleteDocument(filename: string): Promise<{status: string, message: string}> {
  const response = await api.delete(`/documents/${encodeURIComponent(filename)}`)
  return response.data
}
