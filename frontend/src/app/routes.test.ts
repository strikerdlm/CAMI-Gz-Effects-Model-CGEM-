import { describe, expect, it } from 'vitest';

import { APP_ROUTES, routeForPath } from './routes';

describe('APP_ROUTES', () => {
  it('registers the exact eight stable application paths', () => {
    expect(APP_ROUTES.map((route) => route.path)).toEqual([
      '/',
      '/simulator',
      '/prediction',
      '/dashboard',
      '/batch',
      '/analysis',
      '/settings',
      '/about',
    ]);
  });

  it('provides unique ids and searchable help metadata for every route', () => {
    const ids = APP_ROUTES.map((route) => route.id);

    expect(new Set(ids).size).toBe(APP_ROUTES.length);
    for (const route of APP_ROUTES) {
      expect(route.keywords.length).toBeGreaterThan(0);
      expect(route.keywords.every((keyword) => keyword.trim().length > 0)).toBe(true);
      expect(route.helpHash).toMatch(/^#/);
    }
  });

  it('resolves registered paths and falls back to overview', () => {
    expect(routeForPath('/prediction').id).toBe('prediction');
    expect(routeForPath('/not-a-route').id).toBe('overview');
  });
});
