<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-center">Login</h3>
        </div>
        <div class="card-body">
          <div v-if="serverStatus === 'offline'" class="alert alert-danger" role="alert">
            <h5 class="alert-heading">Server is not running!</h5>
            <p>Please start the backend server before attempting to login.</p>
            <hr>
            <p class="mb-0">To start the server:</p>
            <ol class="mb-0">
              <li>Open a terminal in the project directory</li>
              <li>Run: <code>python app.py</code></li>
              <li>Wait for the server to start</li>
              <li>Try logging in again</li>
            </ol>
          </div>
          <div v-else-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          <div v-if="serverError" class="alert alert-danger" role="alert">
            {{ serverError }}
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
                :disabled="loading || serverStatus === 'offline'"
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
                :disabled="loading || serverStatus === 'offline'"
              >
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading || serverStatus === 'offline'">
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
import { mapActions, mapGetters } from 'vuex'

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
  computed: {
    ...mapGetters(['getServerError', 'getServerStatus']),
    serverError() {
      return this.getServerError
    },
    serverStatus() {
      return this.getServerStatus
    }
  },
  methods: {
    ...mapActions(['login', 'checkServerStatus']),
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
        if (!this.serverError) {
          this.error = 'Login failed. Please try again.'
        }
      } finally {
        this.loading = false
      }
    }
  },
  async created() {
    await this.checkServerStatus()
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
code {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
}
</style> 