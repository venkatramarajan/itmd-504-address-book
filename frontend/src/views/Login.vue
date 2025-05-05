<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-center">Login</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input
                type="text"
                class="form-control"
                id="username"
                v-model="username"
                required
                :disabled="loading"
              >
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                class="form-control"
                id="password"
                v-model="password"
                required
                :disabled="loading"
              >
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </div>
          </form>
          <div class="mt-3 text-center">
            <router-link to="/register">Don't have an account? Register here</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      this.error = ''
      this.loading = true
      
      try {
        await this.login({
          username: this.username,
          password: this.password
        })
        this.$router.push('/contacts')
      } catch (error) {
        console.error('Login error:', error)
        this.error = error.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.card {
  margin-top: 2rem;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.alert {
  margin-bottom: 1rem;
}
</style> 