import { initDatabase } from './database';

console.log('🚀 Initializing Knowledge Debt database...\n');

initDatabase();

console.log('\n✅ Database initialization complete!');
console.log('📝 You can now run: npm run db:seed (to add sample data)');

