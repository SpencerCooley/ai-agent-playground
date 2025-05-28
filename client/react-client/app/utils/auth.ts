export const isAuthenticated = () => {
  return !!localStorage.getItem('woopdiAuth');
};

export const getAuthToken = () => {
  return localStorage.getItem('woopdiAuth');
};

export const logout = () => {
  localStorage.removeItem('woopdiAuth');
  window.location.href = '/login';
}; 