const Database = require('better-sqlite3');
const db = new Database('C:/Users/Mek Gacor/AppData/Roaming/9router/db/data.sqlite');
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
console.log('Tables:', tables);

for (const t of tables) {
    if (t.name === 'model_aliases' || t.name === 'models' || t.name === 'aliases' || t.name === 'model_map') {
        const columns = db.prepare("PRAGMA table_info(" + t.name + ")").all();
        console.log('Table ' + t.name + ' columns:', columns.map(c => c.name).join(', '));
        const rows = db.prepare("SELECT * FROM " + t.name).all();
        console.log('Rows:', rows);
    }
}
