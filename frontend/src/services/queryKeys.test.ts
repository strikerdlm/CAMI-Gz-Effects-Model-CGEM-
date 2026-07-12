import { describe, expect, it } from 'vitest';
import { queryKeys } from './queryKeys';

describe('queryKeys', () => {
  it('isolates all server state by API base URL', () => {
    expect(queryKeys.health('http://a')).not.toEqual(queryKeys.health('http://b'));
    expect(queryKeys.version('http://a')).not.toEqual(queryKeys.version('http://b'));
    expect(queryKeys.predict('http://a')).not.toEqual(queryKeys.predict('http://b'));
    expect(queryKeys.sweep('http://a')).not.toEqual(queryKeys.sweep('http://b'));
    expect(queryKeys.run('http://a')).not.toEqual(queryKeys.run('http://b'));
  });

  it('includes the sensitivity target in its scoped key', () => {
    expect(queryKeys.sensitivity('http://a', 'hlap_min')).toEqual([
      'cgem', 'http://a', 'sensitivity', 'hlap_min',
    ]);
    expect(queryKeys.sensitivity('http://a', 'hlap_min')).not.toEqual(
      queryKeys.sensitivity('http://a', 'time_to_gloc_s'),
    );
  });

  it('uses the required prefix for query and mutation scopes', () => {
    const keys = [
      queryKeys.health('http://a'), queryKeys.version('http://a'),
      queryKeys.sensitivity('http://a', null), queryKeys.predict('http://a'),
      queryKeys.sweep('http://a'), queryKeys.run('http://a'),
    ];
    keys.forEach((key) => expect(key.slice(0, 2)).toEqual(['cgem', 'http://a']));
  });
});
