import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add retry logic for failed requests
axios.interceptors.response.use(undefined, async (err) => {
  const { config } = err
  if (!config || !config.retry) {
    return Promise.reject(err)
  }
  config.retry -= 1
  const delayRetry = new Promise(resolve => {
    setTimeout(resolve, config.retryDelay || 1000)
  })
  await delayRetry
  return axios(config)
})

export default createStore({
  state: {
    user: null,
    contacts: [],
    users: [],
    serverError: null,
    serverStatus: 'unknown' // 'unknown', 'online', 'offline'
  },
  getters: {
    isLoggedIn: state => !!state.user,
    isAdmin: state => state.user?.is_admin || false,
    getContacts: state => state.contacts,
    getUsers: state => state.users,
    getServerError: state => state.serverError,
    getServerStatus: state => state.serverStatus
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setContacts(state, contacts) {
      state.contacts = contacts
    },
    setUsers(state, users) {
      state.users = users
    },
    setServerError(state, error) {
      state.serverError = error
    },
    clearServerError(state) {
      state.serverError = null
    },
    setServerStatus(state, status) {
      state.serverStatus = status
    },
    addContact(state, contact) {
      state.contacts.push(contact)
    },
    updateContact(state, updatedContact) {
      const index = state.contacts.findIndex(c => c.id === updatedContact.id)
      if (index !== -1) {
        state.contacts.splice(index, 1, updatedContact)
      }
    },
    deleteContact(state, contactId) {
      state.contacts = state.contacts.filter(c => c.id !== contactId)
    }
  },
  actions: {
    async checkServerStatus({ commit }) {
      try {
        await axios.get(`${API_URL}/health`, { timeout: 5000 })
        commit('setServerStatus', 'online')
        commit('clearServerError')
      } catch (error) {
        commit('setServerStatus', 'offline')
        commit('setServerError', 'Server is not running. Please start the backend server.')
      }
    },
    async login({ commit, dispatch }, credentials) {
      try {
        commit('clearServerError')
        console.log('Attempting login with:', credentials)
        
        // Check server status before attempting login
        await dispatch('checkServerStatus')
        if (this.state.serverStatus === 'offline') {
          throw new Error('Server is not running')
        }

        const response = await axios.post(`${API_URL}/login`, credentials, {
          retry: 3,
          retryDelay: 1000
        })
        console.log('Login response:', response.data)
        
        if (response.data.message === 'Logged in successfully') {
          commit('setUser', {
            username: response.data.username,
            is_admin: response.data.is_admin
          })
        }
        return response
      } catch (error) {
        console.error('Login error in store:', error.response?.data || error)
        if (error.code === 'ERR_NETWORK' || error.message === 'Server is not running') {
          commit('setServerStatus', 'offline')
          commit('setServerError', 'Unable to connect to server. Please check if the server is running.')
        } else {
          commit('setServerError', error.response?.data?.error || 'Login failed. Please try again.')
        }
        throw error
      }
    },
    async register({ commit }, credentials) {
      try {
        commit('clearServerError')
        console.log('Attempting registration with:', credentials)
        const response = await axios.post(`${API_URL}/register`, credentials, {
          retry: 3,
          retryDelay: 1000
        })
        console.log('Registration response:', response.data)
        return response
      } catch (error) {
        console.error('Registration error in store:', error.response?.data || error)
        if (error.code === 'ERR_NETWORK') {
          commit('setServerError', 'Unable to connect to server. Please check if the server is running.')
        } else {
          commit('setServerError', error.response?.data?.error || 'Registration failed. Please try again.')
        }
        throw error
      }
    },
    async logout({ commit }) {
      try {
        await axios.get(`${API_URL}/logout`)
        commit('setUser', null)
        commit('setContacts', [])
      } catch (error) {
        console.error('Logout error:', error.response?.data || error)
        throw error
      }
    },
    async fetchContacts({ commit }) {
      try {
        const response = await axios.get(`${API_URL}/contacts`)
        commit('setContacts', response.data)
      } catch (error) {
        throw error
      }
    },
    async createContact({ commit }, contact) {
      try {
        const response = await axios.post(`${API_URL}/contacts`, contact)
        commit('addContact', response.data)
        return response
      } catch (error) {
        throw error
      }
    },
    async updateContact({ commit }, { id, contact }) {
      try {
        const response = await axios.put(`${API_URL}/contacts/${id}`, contact)
        commit('updateContact', response.data)
        return response
      } catch (error) {
        throw error
      }
    },
    async deleteContact({ commit }, contactId) {
      try {
        await axios.delete(`${API_URL}/contacts/${contactId}`)
        commit('deleteContact', contactId)
      } catch (error) {
        throw error
      }
    },
    async fetchUsers({ commit }) {
      try {
        const response = await axios.get(`${API_URL}/users`)
        commit('setUsers', response.data)
      } catch (error) {
        throw error
      }
    },
    async createUser(_, userData) {
      try {
        return await axios.post(`${API_URL}/users`, userData)
      } catch (error) {
        throw error
      }
    }
  }
}) 