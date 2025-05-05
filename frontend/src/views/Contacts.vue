<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Contacts</h2>
      <button class="btn btn-primary" @click="showAddModal = true">
        Add New Contact
      </button>
    </div>

    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contact in contacts" :key="contact.id">
            <td>{{ contact.firstname }} {{ contact.lastname }}</td>
            <td>{{ contact.email }}</td>
            <td>{{ contact.phone }}</td>
            <td>
              {{ contact.street_address }}
              {{ contact.apartment_unit ? `Apt ${contact.apartment_unit}` : '' }}
              {{ contact.city }}, {{ contact.zip_code }}
            </td>
            <td>
              <button class="btn btn-sm btn-info me-2" @click="editContact(contact)">
                Edit
              </button>
              <button class="btn btn-sm btn-danger" @click="deleteContact(contact.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Contact Modal -->
    <div class="modal fade" :class="{ show: showAddModal }" tabindex="-1" v-if="showAddModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingContact ? 'Edit Contact' : 'Add New Contact' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">First Name</label>
                  <input type="text" class="form-control" v-model="form.firstname" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Last Name</label>
                  <input type="text" class="form-control" v-model="form.lastname" required>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="form.email" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="form.phone" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Street Address</label>
                <input type="text" class="form-control" v-model="form.street_address" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Apartment/Unit (Optional)</label>
                <input type="text" class="form-control" v-model="form.apartment_unit">
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">City</label>
                  <input type="text" class="form-control" v-model="form.city" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Zip Code</label>
                  <input type="text" class="form-control" v-model="form.zip_code" required>
                </div>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary">
                  {{ editingContact ? 'Update Contact' : 'Add Contact' }}
                </button>
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
  name: 'Contacts',
  data() {
    return {
      showAddModal: false,
      editingContact: null,
      form: {
        firstname: '',
        lastname: '',
        email: '',
        phone: '',
        street_address: '',
        apartment_unit: '',
        city: '',
        zip_code: ''
      }
    }
  },
  computed: {
    ...mapGetters(['getContacts']),
    contacts() {
      return this.getContacts
    }
  },
  methods: {
    ...mapActions(['fetchContacts', 'createContact', 'updateContact', 'deleteContact']),
    async handleSubmit() {
      try {
        if (this.editingContact) {
          await this.updateContact({
            id: this.editingContact.id,
            contact: this.form
          })
        } else {
          await this.createContact(this.form)
        }
        this.closeModal()
      } catch (error) {
        alert(error.response?.data?.error || 'Operation failed')
      }
    },
    editContact(contact) {
      this.editingContact = contact
      this.form = { ...contact }
      this.showAddModal = true
    },
    async deleteContact(id) {
      if (confirm('Are you sure you want to delete this contact?')) {
        try {
          await this.deleteContact(id)
        } catch (error) {
          alert(error.response?.data?.error || 'Failed to delete contact')
        }
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingContact = null
      this.form = {
        firstname: '',
        lastname: '',
        email: '',
        phone: '',
        street_address: '',
        apartment_unit: '',
        city: '',
        zip_code: ''
      }
    }
  },
  created() {
    this.fetchContacts()
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