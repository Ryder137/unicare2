from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import traceback
from sqlalchemy import inspect

# Initialize Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///unicare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models (same as in create_tables_simple.py)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    appointment_type = db.Column(db.String(100))
    professional_type = db.Column(db.String(50))
    professional_id = db.Column(db.Integer)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

def check_database():
    with app.app_context():
        try:
            print("="*50)
            print("DATABASE CONNECTION CHECK")
            print("="*50)
            
            # Test database connection
            print("\nTesting database connection...")
            try:
                db.engine.connect()
                print("✅ Successfully connected to the database")
            except Exception as e:
                print(f"❌ Failed to connect to database: {str(e)}")
                return False
                
            # Check if tables exist
            print("\nChecking database tables...")
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Get all table names
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nFound {len(tables)} table(s): {', '.join(tables) if tables else 'None'}")
            
            if not tables:
                print("\n⚠️  No tables found in the database. Did you run the setup script?")
                return False
            
            # Check if our tables exist
            if 'users' in tables:
                print("\n" + "-"*50)
                print("USERS TABLE")
                print("-"*50)
                
                # Get table info
                columns = inspector.get_columns('users')
                print(f"\nTable structure ({len(columns)} columns):")
                for i, column in enumerate(columns, 1):
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    default = f" DEFAULT {column['default']}" if column.get('default') is not None else ""
                    print(f"  {i}. {column['name']:20} {str(column['type']):15} {nullable}{default}")
                
                # Count users
                try:
                    user_count = db.session.query(User).count()
                    print(f"\nTotal users: {user_count}")
                    
                    # List admin users
                    admins = User.query.filter_by(is_admin=True).all()
                    if admins:
                        print("\nAdmin users:")
                        for i, admin in enumerate(admins, 1):
                            print(f"  {i}. {admin.email} ({admin.first_name} {admin.last_name})")
                    else:
                        print("\n⚠️  No admin users found. Please create an admin account.")
                        
                except Exception as e:
                    print(f"\n❌ Error querying users table: {str(e)}")
                    traceback.print_exc()
            
            if 'appointments' in tables:
                print("\n" + "-"*50)
                print("APPOINTMENTS TABLE")
                print("-"*50)
                
                # Get table info
                columns = inspector.get_columns('appointments')
                print(f"\nTable structure ({len(columns)} columns):")
                for i, column in enumerate(columns, 1):
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    default = f" DEFAULT {column['default']}" if column.get('default') is not None else ""
                    fk = ""
                    if column['name'] in ['staff_id', 'student_id']:
                        fk = " (FK: users.id)"
                    print(f"  {i}. {column['name']:20} {str(column['type']):15} {nullable}{default}{fk}")
                
                # Count appointments
                try:
                    appointment_count = db.session.query(Appointment).count()
                    print(f"\nTotal appointments: {appointment_count}")
                    
                    if appointment_count > 0:
                        # Show recent appointments
                        recent_appointments = Appointment.query.order_by(Appointment.start_time.desc()).limit(3).all()
                        print("\nRecent appointments:")
                        for i, appt in enumerate(recent_appointments, 1):
                            print(f"  {i}. {appt.title} - {appt.start_time} ({appt.status})")
                            
                except Exception as e:
                    print(f"\n❌ Error querying appointments table: {str(e)}")
                    traceback.print_exc()
            
            # Check foreign key constraints
            if 'users' in tables and 'appointments' in tables:
                print("\n" + "-"*50)
                print("FOREIGN KEY CHECKS")
                print("-"*50)
                
                try:
                    # Check for appointments without valid users
                    invalid_staff = db.session.query(Appointment).filter(
                        ~Appointment.staff_id.in_(db.session.query(User.id))
                    ).count()
                    
                    invalid_student = db.session.query(Appointment).filter(
                        ~Appointment.student_id.in_(db.session.query(User.id))
                    ).count()
                    
                    if invalid_staff > 0 or invalid_student > 0:
                        print(f"\n⚠️  Found {invalid_staff} appointments with invalid staff_id and {invalid_student} with invalid student_id")
                    else:
                        print("\n✅ All foreign key constraints are valid")
                        
                except Exception as e:
                    print(f"\n❌ Error checking foreign key constraints: {str(e)}")
            
            return True
            
        except Exception as e:
            print("\n" + "="*50)
            print("❌ ERROR CHECKING DATABASE")
            print("="*50)
            print(f"\nError: {str(e)}\n")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("UNICARE DATABASE INTEGRITY CHECK")
    print("="*50)
    
    if check_database():
        print("\n" + "="*50)
        print("✅ DATABASE CHECK COMPLETED SUCCESSFULLY")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ DATABASE CHECK FAILED")
        print("="*50)
        print("\nPlease check the error messages above and ensure the database is properly set up.")
        sys.exit(1)
