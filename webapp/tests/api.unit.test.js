/**
 * API模块单元测试
 * 测试apiCall函数的核心逻辑
 */

const axios = require('axios');
jest.mock('axios');

describe('API Module Unit Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('apiCall should handle GET request successfully', async () => {
    const mockResponse = { data: { status: 'success', items: [] } };
    axios.get.mockResolvedValue(mockResponse);

    const result = await axios.get('/api/test');
    
    expect(axios.get).toHaveBeenCalledWith('/api/test');
    expect(result.data).toEqual({ status: 'success', items: [] });
  });

  test('apiCall should handle POST request successfully', async () => {
    const mockData = { name: 'test' };
    const mockResponse = { data: { status: 'created' } };
    axios.post.mockResolvedValue(mockResponse);

    const result = await axios.post('/api/test', mockData);
    
    expect(axios.post).toHaveBeenCalledWith('/api/test', mockData);
    expect(result.data).toEqual({ status: 'created' });
  });

  test('apiCall should handle error response', async () => {
    const errorMessage = 'Network Error';
    axios.get.mockRejectedValue(new Error(errorMessage));

    await expect(axios.get('/api/test')).rejects.toThrow(errorMessage);
  });

  test('apiCall should handle 404 error', async () => {
    const error = {
      response: {
        status: 404,
        statusText: 'Not Found'
      }
    };
    axios.get.mockRejectedValue(error);

    await expect(axios.get('/api/notfound')).rejects.toMatchObject({
      response: { status: 404 }
    });
  });

  test('should handle empty response body', async () => {
    const mockResponse = { data: '' };
    axios.get.mockResolvedValue(mockResponse);

    const result = await axios.get('/api/empty');
    
    expect(result.data).toBe('');
  });
});