if __name__ == '__main__':
    from .interactive import load, metadata_to_rects, get_svg
    with open('sources.svg', 'w+') as f:
        f.write(get_svg(metadata_to_rects(load('metadata.json'))))

    # import asyncio
    # from .animation import main
    # asyncio.run(main())
