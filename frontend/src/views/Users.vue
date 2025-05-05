<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>User Management</h2>
      <button class="btn btn-primary" @click="showAddModal = true">
        Add New User
      </button>
    </div>

    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Username</th>
            <th>Admin Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.is_admin ? 'Yes' : 'No' }}</td>
            <td>
              <button class="btn btn-sm btn-danger" @click="deleteUser(user.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add User Modal -->
    <div class="modal fade" :class="{ show: showAddModal }" tabindex="-1" v-if="showAddModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New User</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" class="form-control" v-model="form.username" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="form.password" required>
              </div>
              <div class="mb-3">
                <div class="form-check">
                  <input type="checkbox" class="form-check-input" id="isAdmin" v-model="form.is_admin">
                  <label class="form-check-label" for="isAdmin">Admin User</label>
                </div>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary">Add User</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ show: showAddModal }" v-if="showAddModal"></div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Users',
  data() {
    return {
      showAddModal: false,
      form: {
        username: '',
        password: '',
        is_admin: false
      }
    }
  },
  computed: {
    ...mapGetters(['getUsers']),
    users() {
      return this.getUsers
    }
  },
  methods: {
    ...mapActions(['fetchUsers', 'createUser']),
    async handleSubmit() {
      try {
        await this.createUser(this.form)
        this.closeModal()
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to create user')
      }
    },
    closeModal() {
      this.showAddModal = false
      this.form = {
        username: '',
        password: '',
        is_admin: false
      }
    }
  },
  created() {
    this.fetchUsers()
  }
}
</script>

<style scoped>
.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
.modal-backdrop {
  opacity: 0.5;
}
</style> 