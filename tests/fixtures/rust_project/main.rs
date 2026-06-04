use std::env;

fn main() {
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());

    println!("Connecting to {}", database_url);
    println!("Listening on port {}", port);
}
