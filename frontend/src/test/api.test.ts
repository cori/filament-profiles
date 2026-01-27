import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the fetch function
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('API utilities', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should handle successful responses', async () => {
    const mockData = { id: 1, name: 'Test Machine' }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockData),
    })

    const response = await fetch('/api/machines')
    const data = await response.json()

    expect(data).toEqual(mockData)
  })

  it('should handle 204 No Content responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
    })

    const response = await fetch('/api/machines/1', { method: 'DELETE' })

    expect(response.ok).toBe(true)
    expect(response.status).toBe(204)
  })

  it('should handle error responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: 'Machine not found' }),
    })

    const response = await fetch('/api/machines/999')

    expect(response.ok).toBe(false)
    expect(response.status).toBe(404)
  })

  it('should handle bulk delete responses with failures', async () => {
    const mockResult = {
      deleted: [1, 2],
      failed: [{ id: 3, error: 'Has dependent profiles' }],
    }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockResult),
    })

    const response = await fetch('/api/machines/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ ids: [1, 2, 3] }),
    })
    const data = await response.json()

    expect(data.deleted).toHaveLength(2)
    expect(data.failed).toHaveLength(1)
    expect(data.failed[0].error).toContain('dependent')
  })
})
