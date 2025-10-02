-- DIANA - Configuration de la base de données Supabase
-- Exécutez ce script dans l'éditeur SQL de Supabase

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    active_devices TEXT[] DEFAULT '{}',
    max_devices INTEGER DEFAULT 2,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des appareils
CREATE TABLE IF NOT EXISTS user_devices (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    device_name TEXT,
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(device_id)
);

-- Table des logs d'utilisation
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    device_id TEXT,
    action TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_premium ON users(is_premium);
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON user_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON user_devices(device_id);
CREATE INDEX IF NOT EXISTS idx_usage_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_logs(timestamp);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Fonction pour créer automatiquement une entrée utilisateur après inscription
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO users (id, email, is_premium, active_devices, max_devices)
    VALUES (
        NEW.id,
        NEW.email,
        FALSE,
        '{}',
        2
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger après inscription
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- RLS (Row Level Security) - Sécurité au niveau des lignes
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Politique RLS pour users
CREATE POLICY "Users can view own data"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- Politique RLS pour user_devices
CREATE POLICY "Users can view own devices"
    ON user_devices FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own devices"
    ON user_devices FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Politique RLS pour usage_logs
CREATE POLICY "Users can view own logs"
    ON usage_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own logs"
    ON usage_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Vue pour les statistiques utilisateur
CREATE OR REPLACE VIEW user_stats AS
SELECT
    u.id,
    u.email,
    u.is_premium,
    u.created_at,
    ARRAY_LENGTH(u.active_devices, 1) as device_count,
    COUNT(DISTINCT ul.id) as total_analyses,
    MAX(ul.timestamp) as last_activity
FROM users u
LEFT JOIN usage_logs ul ON u.id = ul.user_id AND ul.action = 'prediction'
GROUP BY u.id, u.email, u.is_premium, u.created_at, u.active_devices;

-- Commentaires pour la documentation
COMMENT ON TABLE users IS 'Table des utilisateurs de DIANA';
COMMENT ON TABLE user_devices IS 'Table des appareils enregistrés par utilisateur';
COMMENT ON TABLE usage_logs IS 'Logs d''utilisation de l''application';
COMMENT ON COLUMN users.is_premium IS 'Indique si l''utilisateur a un compte premium';
COMMENT ON COLUMN users.active_devices IS 'Liste des device_id actifs';
COMMENT ON COLUMN users.max_devices IS 'Nombre maximum d''appareils autorisés';

