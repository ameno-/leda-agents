import { validateProfile } from './profile';

type User = {
  profile?: Profile;
};

type Profile = {
  owner?: User;
};

export function validateUser(user: User): boolean {
  return user.profile ? validateProfile(user.profile) : true;
}