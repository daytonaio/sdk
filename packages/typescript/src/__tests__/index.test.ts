import { Daytona } from '../index'

describe('Daytona', () => {
  const validConfig = {
    apiKey: 'test-api-key',
    apiUrl: 'https://api.example.com',
  }

  it('should create an instance with valid config', () => {
    const client = new Daytona(validConfig)
    expect(client).toBeInstanceOf(Daytona)
  })

  it('should throw error when apiKey is missing', () => {
    expect(() => {
      new Daytona({
        ...validConfig,
        apiKey: '',
      })
    }).toThrow('API key is required')
  })

  it('should throw error when apiUrl is missing', () => {
    expect(() => {
      new Daytona({
        ...validConfig,
        apiUrl: '',
      })
    }).toThrow('Server URL is required')
  })
})
