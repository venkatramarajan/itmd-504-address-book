import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.headers.common['Content-Type'] = 'application/json'

export default createStore({
  state: {
    user: null,
    contacts: [],
    users: []
  },
  getters: {
    isLoggedIn: state => !!state.user,
    isAdmin: state => state.user?.is_admin || false,
    getContacts: state => state.contacts,
    getUsers: state => state.users
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
    async login({ commit }, credentials) {
      try {
        console.log('Attempting login with:', credentials)
        const response = await axios.post(`${API_URL}/login`, credentials)
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
        throw error
      }
    },
    async register(_, credentials) {
      try {
        console.log('Attempting registration with:', credentials)
        const response = await axios.post(`${API_URL}/register`, credentials)
        console.log('Registration response:', response.data)
        return response
      } catch (error) {
        console.error('Registration error in store:', error.response?.data || error)
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