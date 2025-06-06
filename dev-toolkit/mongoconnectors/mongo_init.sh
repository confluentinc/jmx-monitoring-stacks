#!/bin/bash

docker exec -i mongo mongosh << EOF
  use admin

  db.createRole({
     role: "confluentCDCRole",
     privileges: [
        { resource: { cluster: true }, actions: ["find", "changeStream"] },
        { resource: { db: "Employee", collection: "users" }, actions: ["find", "changeStream", "insert", "remove", "update"] }
     ],
     roles: []
  });

  db.createUser({
    user: "data-platform-cdc",
    pwd: "password",
    roles: [
      { role: "read", db: "admin" },
      { role: "clusterMonitor", db: "admin" },
      { role: "read", db: "config" },
      { role: "readWrite", db: "Employee" },
      { role: "confluentCDCRole", db: "admin" }
    ]
  });

  use Employee
  db.users.insert([
  {
    "name": "John",
    "surname": "Doe",
    "city": "Albany"
  },
  {
    "name": "Pat",
    "surname": "Erwing",
    "city": "Ney York City"
    }
  ]);

EOF