#!/bin/bash

docker exec -i mongo mongosh << EOF


  use Employee
  db.users.find().pretty();
  db.accounts.find().pretty();

EOF
