import { validateUser } from './validator';

type User = {
  profile?: Profile;
};

type Profile = {
  owner?: User;
};

export function validateProfile(profile: Profile): boolean {
  return profile.owner ? validateUser(profile.owner) : true;
}