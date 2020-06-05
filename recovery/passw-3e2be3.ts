base = {};

ids = [];

interface User {
  username: string
  salt: string
  stretchFactor: number
  hash: string
  id: number
}

function login(username: string, password: string)
{
  if (username in Object.keys(base)) {
    return false;
  }

}
