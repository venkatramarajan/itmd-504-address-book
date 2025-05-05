<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-center">Register</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          <form @submit.prevent="handleRegister">
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
            <div class="mb-3">
              <label for="confirmPassword" class="form-label">Confirm Password</label>
              <input
                type="password"
                class="form-control"
                id="confirmPassword"
                v-model="confirmPassword"
                required
                :disabled="loading"
              >
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </div>
          </form>
          <div class="mt-3 text-center">
            <router-link to="/login">Already have an account? Login here</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      error: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['register']),
    async handleRegister() {
      this.error = ''
      
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }

      if (this.password.length < 6) {
        this.error = 'Password must be at least 6 characters long'
        return
      }

      this.loading = true
      try {
        await this.register({
          username: this.username,
          password: this.password
        })
        this.$router.push('/login')
      } catch (error) {
        console.error('Registration error:', error)
        this.error = error.response?.data?.error || 'Registration failed. Please try again.'
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