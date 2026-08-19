import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {api, ApiError} from './api';

describe('Client API et expiration JWT', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('efface le jeton et avertit l’application à la réception d’un 401', async () => {
    localStorage.setItem('token', 'jwt-expiré');
    const unauthorized = vi.fn();
    window.addEventListener('skilltrack:unauthorized', unauthorized, {once: true});
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        status: 401,
        ok: false,
        json: vi.fn().mockResolvedValue({detail: 'Jeton expiré'}),
        text: vi.fn().mockResolvedValue(''),
        headers: {get: vi.fn().mockReturnValue('application/json')},
      }),
    );

    await expect(api('/dashboard')).rejects.toEqual(
      expect.objectContaining({name: 'ApiError', message: 'Jeton expiré', status: 401}),
    );
    expect(ApiError.prototype).toBeInstanceOf(Error);
    expect(localStorage.getItem('token')).toBeNull();
    expect(unauthorized).toHaveBeenCalledOnce();
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/dashboard',
      expect.objectContaining({headers: {Authorization: 'Bearer jwt-expiré'}}),
    );
  });
});
