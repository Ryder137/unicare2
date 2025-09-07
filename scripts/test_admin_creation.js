// This script tests creating an admin user using the Supabase JavaScript client
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://rzktipnfmqrhpqtlfixp.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY;

if (!SUPABASE_KEY) {
  console.error('Error: SUPABASE_SERVICE_KEY or SUPABASE_KEY environment variable is required');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function createAdminUser() {
  const email = 'test-admin@example.com';
  const password = 'test1234';
  const fullName = 'Test Admin';

  try {
    // First, sign up the user in the auth.users table
    const { data: authData, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
    });

    if (signUpError) {
      console.error('Error signing up user:', signUpError);
      return;
    }

    console.log('Auth user created:', authData.user.id);

    // Then, create a corresponding admin user
    const { data: adminData, error: adminError } = await supabase
      .from('admin_users')
      .insert([
        { 
          id: authData.user.id,
          email,
          full_name: fullName,
          is_active: true,
          is_super_admin: false
        }
      ])
      .select();

    if (adminError) {
      console.error('Error creating admin user:', adminError);
      return;
    }

    console.log('Admin user created successfully:', adminData);
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

createAdminUser();
