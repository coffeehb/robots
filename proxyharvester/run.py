import harvester

if __name__ == '__main__':
    fullpath = os.path.join(os.path.dirname(__file__), 'proxies.p')
    harvester.main(fullpath)